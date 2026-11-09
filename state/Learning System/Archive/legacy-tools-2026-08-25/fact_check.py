"""
fact_check — Learning System teaching fact-check tool for Open WebUI.

Verifies load-bearing factual claims before the tutor presents them during a
teaching session (/lesson, teach me X). Calls a SECOND, cheaper model —
whatever is set on this tool's `fact_check_model` Valve — so the tutor model
does not grade its own claims.

The tutor passes the claim plus the source it is teaching from (an excerpt of
RESOURCES.md, the course source, or a fetched URL). The checker returns a
verdict plus a corrected version when the claim is wrong.

This is the teaching-path verifier. The ingest quality gate is the separate
`review_gate` tool — the two verification paths stay separate.

MODELS: after install, the fact-check model is changed in ONE place — this
tool's Valves (Workspace → Tools → fact_check → ⚙). See OPENWEBUI.md. The
hardcoded id below is a bootstrap fallback only (env FACT_CHECK_MODEL overrides).

INSTALL
-------
1. Open WebUI → Workspace → Tools → "+" (Create Tool).
2. Paste this whole file, name it "fact_check", Save.
3. Enable the tool for the Learning Tutor model (Workspace → Models → Edit → Tools).
4. Set the Valves: base URL, API key, fact_check_model.
"""

import asyncio
import json
import os
import re
from datetime import datetime, timezone

try:
    from pydantic import BaseModel, Field
except Exception:
    BaseModel = None
    Field = None

try:
    from open_webui.tools import tools
except Exception:
    def tools(fn):
        return fn


def _make_valves_class():
    """Build the Valves class. If pydantic is unavailable, fall back to a plain
    dict-like so the tool still loads (valves simply won't be validated)."""
    if BaseModel is not None and Field is not None:
        class Valves(BaseModel):
            openwebui_base_url: str = Field(
                default=os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:8080"),
                description="Open WebUI base URL as seen from inside this container, e.g. http://localhost:8080",
            )
            openwebui_api_key: str = Field(
                default=os.environ.get("OPENWEBUI_API_KEY", ""),
                description="API key (Admin → API Keys). Falls back to env OPENWEBUI_API_KEY.",
            )
            fact_check_model: str = Field(
                default=os.environ.get("FACT_CHECK_MODEL", "ox-alpha-free"),
                description="Fact-check model id (bootstrap fallback — change in UI Valves). Should be a different model than the tutor.",
            )
            timeout: int = Field(default=150, description="HTTP timeout in seconds.")
        return Valves

    class Valves:  # noqa: F811
        pass
    return Valves

FACT_CHECK_TEMPLATE = """# Learning System — Fact Check (fixed template)

You are an independent fact-checker for a learning system. A tutor is about to
teach a learner a claim. Your job is to verify the claim against the provided
reference material (and your own knowledge) and return a verdict. You are a
critic, not a rewrite bot: flag problems concisely, never rewrite the lesson.

## Inputs

- CLAIM TO VERIFY:
{claim}

- REFERENCE TEXT (what the tutor is teaching from; may be partial — do not
  penalize the claim for facts simply not covered here):
{reference}

- SOURCE URL (if any; the checker fetched it):
{source_url}
{source_content}

- CONTEXT (what the tutor is doing, e.g. "explaining make timestamps in a
  Stage-0 SWE lesson"):
{context}

## Rules

- Verdict PASS when the claim is correct and would not mislead the learner.
- Verdict ISSUES when the claim is wrong, subtly misleading, or contradicts the
  reference. Be strict about mechanism-level claims (how something works), less
  strict about phrasing.
- If the reference is silent on the claim, check against your own knowledge.
  If you are genuinely unsure, note it as UNVERIFIED rather than guessing.
- Do not invent sources. Do not penalize missing formatting.
- Output ONLY valid JSON — a single JSON object, no prose before or after it,
  no leading newline, no trailing text:

```json
{{
  "verdict": "PASS" | "ISSUES" | "UNVERIFIED",
  "explanation": "one short paragraph: why pass, what is wrong, or what is unverified",
  "corrected_claim": "only when ISSUES — a corrected, teachable version of the claim; otherwise null"
}}
```"""


def _http_get(url, timeout):
    """Fetch a URL. Tries requests, then urllib (stdlib) as fallback."""
    try:
        import requests  # noqa
        resp = requests.get(url, timeout=timeout)
        return resp.status_code, resp.text
    except Exception:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "fact_check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")


def _http_post_json(url, payload, api_key, timeout):
    """POST JSON to the Open WebUI chat-completions API."""
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        import requests  # noqa
        resp = requests.post(url, data=body, headers=headers, timeout=timeout)
        return resp.status_code, resp.text
    except Exception:
        import urllib.request
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")


def _extract_json(text):
    """Pull a JSON object out of a model response.

    Handles: clean JSON, code-fenced JSON, prose around JSON, and the common
    failure where the model returns a bare fragment like
        \\n"verdict": "ISSUES", ...
    (no wrapping braces). The fragment is wrapped and repaired.
    """
    text = text.strip()

    # 1. Clean JSON on its own.
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2. Code-fenced JSON.
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except Exception:
            pass

    # 3. A real `{...}` object somewhere in the text (wrapped or in prose).
    #    Skip when the text is a bare JSON fragment starting with `"`, where the
    #    first `{` belongs to a nested array, not the object root.
    if not text.startswith('"'):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

    # 4. Bare fragment without wrapping braces. Wrap and ensure it closes.
    fragment = text.strip()
    if fragment:
        wrapped = "{" + fragment
        if not wrapped.rstrip().endswith("}"):
            wrapped = wrapped.rstrip().rstrip(",") + "}"
        try:
            return json.loads(wrapped)
        except Exception:
            pass

    raise ValueError(f"Fact-check model did not return valid JSON: {text[:500]}")


class Tools:
    def __init__(self):
        self.valves = self.Valves()

    class Valves(_make_valves_class()):
        pass

    @tools
    async def fact_check(self, claim: str, reference: str = "", source_url: str = "", context: str = "") -> str:
        """
        Verify a load-bearing claim before teaching it.
        claim: the exact claim to verify (required).
        reference: excerpt of the source the tutor is teaching from (RESOURCES.md, course text).
        source_url: optional URL to fetch and check the claim against.
        context: what the tutor is doing, to disambiguate.
        Returns verdict JSON (PASS / ISSUES / UNVERIFIED) with a corrected claim when ISSUES.
        """
        valves = getattr(self, "valves", None)
        base_url = getattr(valves, "openwebui_base_url", "") or os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:8080")
        api_key = getattr(valves, "openwebui_api_key", "") or os.environ.get("OPENWEBUI_API_KEY", "")
        model = getattr(valves, "fact_check_model", "") or os.environ.get("FACT_CHECK_MODEL", "ox-alpha-free")
        timeout = getattr(valves, "timeout", 90)

        if not claim.strip():
            return json.dumps({"error": "no claim given"}, indent=2)

        source_content = ""
        if source_url:
            try:
                status, content = await asyncio.to_thread(_http_get, source_url, timeout)
                if status < 400:
                    source_content = f"\n- FETCHED SOURCE CONTENT (HTTP {status}):\n{content[:20000]}"
                else:
                    source_content = f"\n- SOURCE URL returned HTTP {status}; ignored.\n"
            except Exception as e:
                source_content = f"\n- SOURCE URL could not be fetched: {e}\n"

        prompt = FACT_CHECK_TEMPLATE.format(
            claim=claim,
            reference=reference or "(none provided — check against your own knowledge)",
            source_url=source_url or "(none)",
            source_content=source_content,
            context=context or "(none)",
        )

        if not api_key:
            return json.dumps(
                {"error": "no API key configured — set the Valve or env OPENWEBUI_API_KEY"},
                indent=2,
            )
        url = base_url.rstrip("/") + "/api/chat/completions"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        try:
            # Run the blocking HTTP call in a worker thread so the event loop stays
            # free to serve the nested /api/chat/completions request (avoids a
            # self-call deadlock where the tool waits on its own worker).
            status, resp_text = await asyncio.to_thread(_http_post_json, url, payload, api_key, timeout)
        except Exception as e:
            return json.dumps({"error": f"fact-check model call failed: {e}"}, indent=2)
        if status >= 400:
            return json.dumps(
                {"error": f"fact-check model call returned HTTP {status}: {resp_text[:500]}"},
                indent=2,
            )
        try:
            data = json.loads(resp_text)
            verdict = _extract_json(data["choices"][0]["message"]["content"])
        except Exception as e:
            return json.dumps({"error": f"could not parse fact-check model response: {e}"}, indent=2)

        return json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "claim": claim,
                "model": model,
                "verdict": verdict,
            },
            indent=2,
        )