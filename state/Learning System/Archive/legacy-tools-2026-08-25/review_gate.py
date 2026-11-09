"""
review_gate — Learning System ingest quality gate for Open WebUI.

Runs the independent review gate defined in Skills/learning-review/SKILL.md:
  - fetches the source URL itself (dead URL aborts with an error)
  - builds the review prompt from a FIXED template (never editable at runtime)
  - calls a SECOND model — whatever is set on this tool's `review_model`
    Valve — via the Open WebUI chat-completions API as the independent reviewer
  - returns the verdict JSON, which the chat saves to
    Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json

The repo lives in the Open Terminal sandbox (/home/user/learning-system), a
different container from this one, so the wiki text is passed in directly as
`wiki_content` (the model reads the files via the terminal and passes them in).

MODELS: after install, the reviewer model is changed in ONE place — this tool's
Valves (Workspace → Tools → review_gate → ⚙). See OPENWEBUI.md. The hardcoded
id below is a bootstrap fallback only (env REVIEW_GATE_MODEL overrides it).

INSTALL
-------
1. Open WebUI → Workspace → Tools → "+" (Create Tool).
2. Paste this whole file, name it "review_gate", Save.
3. Enable the tool for the Learning Tutor model (Workspace → Models → Edit → Tools).
4. Set the Valves (gear icon): base URL, an API key, and the review model id.

Then after an ingest (or at lesson end when the lesson wrote wiki content), say:
run the review gate on <concepts> from <source>.
The model passes the wiki content it wrote (read via the terminal).
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
            review_model: str = Field(
                default=os.environ.get("REVIEW_GATE_MODEL", "ox-alpha-free"),
                description="Review model id (bootstrap fallback — change in UI Valves). Must be a different model than the chat model.",
            )
            timeout: int = Field(default=150, description="HTTP timeout in seconds.")
        return Valves

    class Valves:  # noqa: F811
        pass
    return Valves

# --------------------------------------------------------------------------
# Fixed review prompt. Keep in sync with
# Skills/learning-review/templates/review.template.md (the canonical copy).
# This embedded copy is what runs inside Open WebUI, since the repo is not on
# this server's filesystem.
# --------------------------------------------------------------------------
REVIEW_TEMPLATE = """# Learning System Review Gate — Review Prompt (fixed template)

You are an independent, critical reviewer for a spaced-repetition learning system.
Your job is to catch problems in ingest output. You are a critic, not a rewrite bot:
never rewrite content, only flag issues with severity.

## Inputs

- SOURCE URL: {source}
- SOURCE CONTENT (fetched from the URL; if empty, say so and review for internal consistency only):
{source_content}

- CONCEPTS: {concepts}
- WIKI CONTENT (the ingest output being reviewed):
{wiki_content}

- PASS (cycle): {pass_number}

## Scope

Review ONLY:
1. The wiki content above.
2. The Active Concepts insight rows / question seeds derived from this ingest.

Mechanical date updates and review session notes are out of scope.

## What to check

1. **Accuracy / correctness** — claims that contradict the source content, wrong mechanisms, wrong formulas or definitions, invented facts.
2. **Clarity** — phrasing that would mislead a learner or is so ambiguous it fails to teach.
3. **Completeness** — load-bearing points from the source that were dropped or misrepresented.

## Rules

- Only flag issues worth fixing. High/medium severity only; low-severity nits get one combined note.
- Each issue: severity (high | medium | low), location (file/section), issue (specific and actionable).
- Material in the wiki content that is NOT present in the source must be flagged as a scope problem unless a scope note explains the addition.
- Output ONLY valid JSON — a single JSON object
  No prose before or after, no leading newline, no trailing text. Schema:

```json
{{
  "verdict": "PASS" | "ISSUES",
  "issues": [
    {{ "severity": "high|medium|low", "location": "...", "issue": "..." }}
  ]
}}
```

- `"verdict": "PASS"` only when there are no high/medium issues."""


def _http_get(url, timeout):
    """Fetch a URL. Tries requests, then urllib (stdlib) as fallback."""
    try:
        import requests  # noqa
        resp = requests.get(url, timeout=timeout)
        return resp.status_code, resp.text
    except Exception:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "review_gate/1.0"})
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
        \\n"verdict": "ISSUES", "issues": [...]
    (no wrapping braces). The fragment is wrapped and repaired so the gate
    still gets a usable verdict.
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

    # 3. A real `{...}` object somewhere in the text (either wrapped by the
    #    model or embedded in prose). Skip this when the text is a bare JSON
    #    fragment that starts with `"` — there the first `{` belongs to a nested
    #    array, not the object root.
    if not text.startswith('"'):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

    # 4. Bare fragment without wrapping braces, e.g. a leading newline then
    #    `"verdict": "..."`. Wrap it in braces and ensure it closes.
    fragment = text.strip()
    if fragment:
        wrapped = "{" + fragment
        if not wrapped.rstrip().endswith("}"):
            wrapped = wrapped.rstrip().rstrip(",") + "}"
        try:
            return json.loads(wrapped)
        except Exception:
            pass

    raise ValueError(f"Review model did not return valid JSON: {text[:500]}")


class Tools:
    def __init__(self):
        self.valves = self.Valves()

    class Valves(_make_valves_class()):
        pass

    @tools
    async def review_gate(self, source: str, concepts: str, wiki_content: str, pass_number: int = 1) -> str:
        """
        Run the independent review gate on learning-system ingest output.
        source: URL the ingest came from (must be a live, stable URL).
        concepts: comma-separated concept names.
        wiki_content: the full text of the wiki page(s) produced by the ingest
            (read the files via the terminal and pass their content here).
        pass_number: cycle number (1 or 2) — filename only, never softens the review.
        Returns verdict JSON; save it to Learning System/Reviews/Quality Gates/.
        """
        valves = getattr(self, "valves", None)
        base_url = getattr(valves, "openwebui_base_url", "") or os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:8080")
        api_key = getattr(valves, "openwebui_api_key", "") or os.environ.get("OPENWEBUI_API_KEY", "")
        model = getattr(valves, "review_model", "") or os.environ.get("REVIEW_GATE_MODEL", "ox-alpha-free")
        timeout = getattr(valves, "timeout", 90)

        concept_list = [c.strip() for c in concepts.split(",") if c.strip()]

        if not concept_list:
            return json.dumps({"error": "no concepts given"}, indent=2)
        if not wiki_content.strip():
            return json.dumps({"error": "no wiki content given — read the wiki file(s) and pass their text"}, indent=2)

        # 1. Fetch source (dead URL aborts — no verdict written).
        try:
            status, source_content = await asyncio.to_thread(_http_get, source, timeout)
            if status >= 400:
                return json.dumps(
                    {"error": f"source URL returned HTTP {status} — aborting, no verdict written", "source": source},
                    indent=2,
                )
        except Exception as e:
            return json.dumps(
                {"error": f"could not fetch source URL — aborting, no verdict written: {e}", "source": source},
                indent=2,
            )

        # 2. Build the fixed prompt.
        prompt = REVIEW_TEMPLATE.format(
            source=source,
            source_content=source_content[:60000],
            concepts=", ".join(concept_list),
            wiki_content=wiki_content[:120000],
            pass_number=pass_number,
        )

        # 3. Call the review model via Open WebUI chat-completions.
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
            return json.dumps({"error": f"review model call failed: {e}"}, indent=2)
        if status >= 400:
            return json.dumps(
                {"error": f"review model call returned HTTP {status}: {resp_text[:500]}"},
                indent=2,
            )
        try:
            data = json.loads(resp_text)
            verdict = _extract_json(data["choices"][0]["message"]["content"])
        except Exception as e:
            return json.dumps({"error": f"could not parse review model response: {e}"}, indent=2)

        # 4. Return verdict JSON in the repo's existing schema.
        return json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "source": source,
                "concepts": concept_list,
                "pass": str(pass_number),
                "model": model,
                "verdict": verdict,
            },
            indent=2,
        )