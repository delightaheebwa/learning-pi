"""
quiz_gate — Learning System quiz quality gate for Open WebUI.

Runs the independent quiz audit defined in Skills/learning-teach/SKILL.md:
  - validates the submitted question batch mechanically (schema, option count,
    correct-index bounds) BEFORE spending a model call
  - builds the audit prompt from a FIXED template (never editable at runtime)
  - calls a SECOND model — whatever is set on this tool's `quiz_model` Valve —
    via the Open WebUI chat-completions API as the independent quiz auditor
  - returns the verdict JSON to the chat

Used for BOTH the probe (find-the-edge phase) and the end-of-lesson quiz.
The gate audits quality only — it never sees learner answers, so it cannot
leak an answer key into the conversation.

The repo lives in the Open Terminal sandbox (/home/user/learning-system), a
different container from this one, so the source excerpt is passed in directly.

MODELS: after install, the quiz-audit model is changed in ONE place — this
tool's Valves (Workspace → Tools → quiz_gate → ⚙). See OPENWEBUI.md. The
hardcoded id below is a bootstrap fallback only (env QUIZ_GATE_MODEL overrides).

INSTALL
-------
1. Open WebUI → Workspace → Tools → "+" (Create Tool).
2. Paste this whole file, name it "quiz_gate", Save.
3. Enable the tool for the Learning Tutor model (Workspace → Models → Edit → Tools).
4. Set the Valves (gear icon): base URL, an API key, and the quiz model id.

Then during probing (or before the end-of-lesson quiz): build the full question
batch as JSON and call quiz_gate before showing anything to the user.
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
            quiz_model: str = Field(
                default=os.environ.get("QUIZ_GATE_MODEL", "ox-alpha-free"),
                description="Quiz-audit model id (bootstrap fallback — change in UI Valves). Must be a different model than the chat model.",
            )
            timeout: int = Field(default=150, description="HTTP timeout in seconds.")
        return Valves

    class Valves:  # noqa: F811
        pass
    return Valves

# --------------------------------------------------------------------------
# Fixed audit prompt. This embedded copy is what runs inside Open WebUI,
# since the repo is not on this server's filesystem.
# --------------------------------------------------------------------------
QUIZ_TEMPLATE = """# Learning System Quiz Gate — Audit Prompt (fixed template)

You are an independent, critical quiz auditor for a spaced-repetition learning
system. A tutor wrote a batch of questions to measure what a learner actually
knows. Your job is to find every way a GUESSER — someone with no knowledge of
the topic — could get items right, and every flaw that lets the correct answer
be inferred without knowledge. You are a critic: flag issues with severity and
suggest concrete fixes; never rewrite the whole batch yourself.

## Inputs

- PURPOSE (probe find-the-edge | end-of-lesson quiz): {purpose}
- CONCEPT / TOPIC: {concept}
- TARGET BLOOM LEVELS: {bloom_levels}
- SOURCE EXCERPT (what the questions should be grounded in):
{source_excerpt}

- QUESTION BATCH (JSON; `correct_index` is the tutor's private key — audit it,
  never echo it back in suggested fixes):
{questions_json}

## What to check — every multiple-choice item

1. **Length/shape symmetry** — the correct option must not be the longest or
   shortest, nor the only one with extra detail or qualifiers.
2. **Stem echo** — the correct option must not restate the question's phrasing
   or contain a term the stem sets up as the answer.
3. **Only-defensible-option test** — cover the key: could a knowledgeable person
   defend each distractor briefly? If any distractor is trivially discardable
   without knowledge, that is a HIGH issue.
4. **Distractor strength taxonomy** — the set should mix: almost-right (one term
   swapped / one step off), right-in-another-context, right-under-a-different
   condition, missing-a-qualifier. Flag homogeneous or joke distractors.
5. **Parallel grammar** — same part of speech, same tense, no qualifiers like
   "usually"/"primarily" attached only to the true option.
6. **No all/none-of-the-above.**
7. **Textbook echo** — correct option must not quote the source excerpt verbatim
   while distractors are paraphrased.
8. **Self-contained stem** — the answer must not be stated in the stem.

## What to check — free-recall items

9. The prompt must not telegraph the answer in its own wording.
10. It must be gradeable against the source excerpt (or general knowledge) with
    an objective core of facts, not pure opinion.

## Batch-level checks

11. **Position distribution** — correct answers must not cluster in one slot;
    flag if one position holds noticeably more than chance across the batch.
12. **Difficulty vs Bloom level** — items targeting Apply+ should not be simple
    definitional recall dressed as MCQ.
13. **Coverage** — do the items actually triangulate the stated concept/topic?

## Guessability

For EACH item give a guessability rating: low (a guesser has no edge),
medium (weak distractor gives some edge), high (answer inferable without
knowledge).

## Rules

- Only flag issues worth fixing. High/medium severity individually; low-severity
  nits combined in one note per item.
- Suggested fixes must NOT reveal which slot is correct ("swap option C into a
  distractor" style guidance is fine).
- Output ONLY valid JSON — a single JSON object, no prose before or after, no
  leading newline, no trailing text. Schema:

```json
{{
  "verdict": "PASS" | "ISSUES",
  "items": [
    {{
      "id": "<item id>",
      "type": "mcq" | "free_recall",
      "guessability": "low" | "medium" | "high",
      "issues": [
        {{ "severity": "high|medium|low", "issue": "...", "suggested_fix": "..." }}
      ]
    }}
  ],
  "batch_notes": ["position distribution, coverage, difficulty notes"]
}}
```

- `"verdict": "PASS"` only when there are NO high/medium issues AND no item is
  rated high guessability."""


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

    # 3. A real `{...}` object somewhere in the text. Skip when the text is a
    #    bare fragment starting with `"` (the first `{` belongs to a nested
    #    array, not the object root).
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

    raise ValueError(f"Quiz-audit model did not return valid JSON: {text[:500]}")


def _validate_batch(questions):
    """Mechanical pre-flight checks. Returns (ok, error_message, normalized).

    Guards against malformed batches BEFORE any model call: wrong types,
    too-few options, out-of-range correct_index, missing ids/questions.
    """
    if not isinstance(questions, list) or not questions:
        return False, "questions must be a non-empty JSON array", None

    positions = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            return False, f"item {i}: not an object", None
        qtype = q.get("type", "mcq")
        if qtype not in ("mcq", "free_recall"):
            return False, f"item {i}: unknown type '{qtype}' (mcq | free_recall)", None
        if not str(q.get("question", "")).strip():
            return False, f"item {i}: empty question text", None
        if q.get("id") in (None, ""):
            q["id"] = f"q{i + 1}"
        if qtype == "mcq":
            options = q.get("options")
            if not isinstance(options, list) or len(options) < 3:
                return False, f"item {i} ({q.get('id')}): mcq needs at least 3 options", None
            ci = q.get("correct_index")
            if not isinstance(ci, int) or not (0 <= ci < len(options)):
                return False, f"item {i} ({q.get('id')}): correct_index out of range", None
            positions.append(ci)

    # Position clustering warning is left to the auditor; but a batch where the
    # key is trivially uniform (all identical slots) fails mechanically.
    if len(positions) >= 3 and len(set(positions)) == 1:
        return False, (
            f"every correct answer sits in the same slot ({positions[0]}) — "
            "rebalance positions before submitting"
        ), None

    return True, "", questions


class Tools:
    def __init__(self):
        self.valves = self.Valves()

    class Valves(_make_valves_class()):
        pass

    @tools
    async def quiz_gate(self, questions_json: str, purpose: str = "probe", concept: str = "", bloom_levels: str = "", source_excerpt: str = "") -> str:
        """
        Run the independent quiz-quality gate on a question batch BEFORE presenting it.
        questions_json: JSON array of items. MCQ item: {"id","type":"mcq","question",
            "options":[...],"correct_index":<int>,"target_bloom":"..."}. Free-recall item:
            {"id","type":"free_recall","question":"...","target_bloom":"..."}.
        purpose: "probe" or "end-of-lesson quiz".
        concept: concept or topic being probed. bloom_levels: targeted Bloom levels.
        source_excerpt: source text the questions should be grounded in.
        Returns verdict JSON (PASS / ISSUES with per-item fixes). Fix high/medium
        issues and re-run; max 2 cycles before surfacing to the user.
        """
        valves = getattr(self, "valves", None)
        base_url = getattr(valves, "openwebui_base_url", "") or os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:8080")
        api_key = getattr(valves, "openwebui_api_key", "") or os.environ.get("OPENWEBUI_API_KEY", "")
        model = getattr(valves, "quiz_model", "") or os.environ.get("QUIZ_GATE_MODEL", "ox-alpha-free")
        timeout = getattr(valves, "timeout", 150)

        # 1. Mechanical validation — no model call on malformed input.
        try:
            questions = json.loads(questions_json)
        except Exception as e:
            return json.dumps({"error": f"questions_json is not valid JSON: {e}"}, indent=2)
        ok, err, questions = _validate_batch(questions)
        if not ok:
            return json.dumps({"error": err}, indent=2)

        # 2. Build the fixed prompt.
        prompt = QUIZ_TEMPLATE.format(
            purpose=purpose or "(not given)",
            concept=concept or "(not given)",
            bloom_levels=bloom_levels or "(not given)",
            source_excerpt=source_excerpt[:40000] or "(none provided)",
            questions_json=json.dumps(questions, indent=2)[:60000],
        )

        # 3. Call the quiz-audit model via Open WebUI chat-completions.
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
            return json.dumps({"error": f"quiz-audit model call failed: {e}"}, indent=2)
        if status >= 400:
            return json.dumps(
                {"error": f"quiz-audit model call returned HTTP {status}: {resp_text[:500]}"},
                indent=2,
            )
        try:
            data = json.loads(resp_text)
            verdict = _extract_json(data["choices"][0]["message"]["content"])
        except Exception as e:
            return json.dumps({"error": f"could not parse quiz-audit model response: {e}"}, indent=2)

        # 4. Return verdict JSON.
        return json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "purpose": purpose,
                "concept": concept,
                "model": model,
                "item_count": len(questions),
                "verdict": verdict,
            },
            indent=2,
        )
