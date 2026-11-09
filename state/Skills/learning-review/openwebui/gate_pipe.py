"""
gate_pipe — Deterministic delegation gate (Open WebUI Filter).

Installed as Filter (Function type filter), bound to Tutor/Clerk/Deputy presets
(Scout exempt). Deputy is the user's review preset, held to clerk-role rules.
Runs as outlet (blocking before render) with inlet pass-through.

Enforces:
- Tutor new-lesson: Scout digest + Scout message present (slug match, 7-day TTL).
  Resume of existing lesson (Lessons/ file exists) bypasses digest check.
- Tutor content (Learning Tutor only, multi-turn): per-generation GATE:fact_check /
  GATE:quiz_audit / GATE:grade_audit receipts — each Tutor generation that teaches
  must have a fresh fact_check (claims) or quiz_audit (questions), and each
  review grade must have a fresh grade_audit, with parent_message_id == draft.id;
  an upfront Plan batch never satisfies later Teach steps, and quiz_audit never
  satisfies claims. Mixed claims+quiz needs BOTH receipts for the same message.
- Clerk content (single-turn): single GATE:review receipt per wiki write; a
  standalone-review close requires a GATE:review_session receipt auditing the
  end-of-review writes (Review notes, session note, touched state rows) — on
  ISSUES after the fix loop the summary renders with a flags banner, never a
  withhold (avoids the pi dead-end).

Retry: outlet replaces blocked draft with BLOCKED (<code>) banner. Cap 2 per
USER TURN (reset when parent user message changes), durably counted in
Chat.meta.gate_state. After cap, withheld banner only.

Digest: Learning System/.tmp/context-<chat_id>-<slug>.json, gitignored.
Expiry 7 days, swept on next Tutor/Clerk inlet.

Install: setup_openwebui.py creates Function and binds filterIds to presets.
"""

import json
import os
import re
import time
from pathlib import Path

try:
    from pydantic import BaseModel, Field
except Exception as e:  # pragma: no cover
    raise ImportError("pydantic is required for gate_pipe — install it or run inside Open WebUI") from e

# --- GATE_SCHEMA_IMPORT_BEGIN (installer inlines gate_schema.py here — do not
# --- change these marker lines; setup_openwebui.py + audit_openwebui.py splice
# --- strictly between them) ---
try:
    from gate_schema import (
        GATEFactCheckEnvelope,
        GATEReviewEnvelope,
        GATEReviewSessionEnvelope,
        GATEQuizAuditEnvelope,
        GATEGradeAuditEnvelope,
        extract_json_block,
    )
except Exception:
    try:
        from open_webui.functions.gate_schema import (  # type: ignore
            GATEFactCheckEnvelope,
            GATEReviewEnvelope,
            GATEReviewSessionEnvelope,
            GATEQuizAuditEnvelope,
            GATEGradeAuditEnvelope,
        )
        from open_webui.functions.gate_schema import extract_json_block  # type: ignore
    except Exception:
        GATEFactCheckEnvelope = None  # type: ignore
        GATEReviewEnvelope = None  # type: ignore
        GATEReviewSessionEnvelope = None  # type: ignore
        GATEQuizAuditEnvelope = None  # type: ignore
        GATEGradeAuditEnvelope = None  # type: ignore
        extract_json_block = lambda t: None  # noqa: E731
# --- GATE_SCHEMA_IMPORT_END ---


TMP_DIR = ".tmp"
SLUG_RE = re.compile(r"[^a-z0-9]+")
TRIGGER_RE = re.compile(r"^\s*(/teach|/lesson|/continue|teach me|learn|study)\b", re.I)
# Per-generation gate (Tutor only): detect quiz vs claims content
_QUIZ_RE = re.compile(r"(\|\s*A\s*\||\|\s*B\s*\||\bQ\s*\d+\b|Your answer \+ confidence|correct_index|questions_json)", re.I)
# Review grading content (Tutor review flow): grade marker + verdict marker.
# Grading lines are short (<=1 line + mastery line) so they would otherwise
# fall under the <120char bypass — detect explicitly before length checks.
_GRADE_MARKER_RE = re.compile(r"(mastery\s+\d|Feynman:|ops\.py\s+attempt|Reviews/Review|Next Review|Last Q Type)", re.I)
_GRADE_VERDICT_RE = re.compile(r"\b(pass|fail|held|advanced|graduated)\b", re.I)


def _is_grade_content(text: str) -> bool:
    s = text or ""
    return bool(_GRADE_MARKER_RE.search(s) and _GRADE_VERDICT_RE.search(s))


# Review-session close: the Clerk's end-of-review summary lists results for
# several concepts (mastery + next review + mistakes/graduation). It is longer
# than a single grade line and carries >=3 review markers. A single grade turn
# is short (<=1 line + mastery line) and stays on the grade_audit path.
_REVIEW_SESSION_MARK_RE = re.compile(
    r"(mastery\s+\d|Next Review|Last Q Type|Reviews/Review|Feynman:|\bgraduated\b)", re.I
)


def _is_review_session_content(text: str) -> bool:
    s = (text or "").strip()
    if len(s) < 200:
        return False
    return len(_REVIEW_SESSION_MARK_RE.findall(s)) >= 3


_REVIEW_SESSION_FLAGS_BANNER = (
    "⚠️ REVIEW FLAGS SURFACED — the end-of-review audit returned high/medium flags on the "
    "session writes (Review notes / session note / touched state rows). The summary below is "
    "shown with those flags outstanding; fix them next session — do not re-run the audit "
    "(hard cap 2 cycles).\n\n"
)


def _is_quiz_content(text: str) -> bool:
    return bool(_QUIZ_RE.search(text or ""))


def _non_quiz_prose_len(text: str) -> int:
    """Chars outside quiz markers/tables — used to distinguish pure quiz vs mixed."""
    total = 0
    for line in text.splitlines():
        if _QUIZ_RE.search(line):
            continue
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        total += len(stripped)
    return total


def _is_claims_content(text: str) -> bool:
    s = (text or "").strip()
    if len(s) < 120:
        return False
    if not _is_quiz_content(s):
        return True

    non_quiz = _non_quiz_prose_len(s)
    hits = len(_QUIZ_RE.findall(s))

    # Pure quiz: several markers but little prose → quiz-only
    if hits >= 3 and non_quiz < 300:
        return False
    if hits >= 2 and non_quiz < 200:
        return False

    # Mixed: quiz markers plus substantial prose → needs fact_check as well
    if non_quiz > 250:
        return True
    return len(s) > 500 and non_quiz > 120


def _gate_needs(content: str, is_tutor: bool, is_clerk: bool):
    """Return (needs_fact_check, needs_quiz_audit, needs_review, needs_grade, needs_review_session)."""
    if is_tutor:
        # Review-session close (multi-concept summary) takes precedence; a single
        # grade line stays on grade_audit. Grading lines are short and would
        # otherwise bypass via <120char or misclassify as fact_check.
        if _is_review_session_content(content):
            return False, False, False, False, True
        if _is_grade_content(content):
            return False, False, False, True, False
        needs_fact = _is_claims_content(content)
        needs_quiz = _is_quiz_content(content)
        if not needs_fact and not needs_quiz and len(content.strip()) > 120:
            needs_fact = True
        return needs_fact, needs_quiz, False, False, False
    if is_clerk and len(content.strip()) > 80:
        # Clerk runs review sessions too (standalone reviews + lesson handoffs):
        # a session close needs review_session, grade turns need grade_audit,
        # wiki-write turns need review.
        if _is_review_session_content(content):
            return False, False, False, False, True
        if _is_grade_content(content):
            return False, False, False, True, False
        return False, False, True, False, False
    return False, False, False, False, False


# Visual fences are not prose. The bridge lifts ```openui out before emission,
# and ```mermaid / ```html render natively in the Open WebUI client; a payload
# must never satisfy a claim or a rendered-vs-output comparison. The language tag
# may carry a trailing info string (` ```openui ... `), so match to end of line.
_VISUAL_FENCE_RE = re.compile(r"```(?:openui|mermaid|html)[^\n]*\n.*?```", re.DOTALL | re.IGNORECASE)


def _normalize_for_binding(text: str) -> str:
    """Normalize for plan-vs-output binding: drop visual fences, lower, collapse
    ws, strip KaTeX markers."""
    s = _VISUAL_FENCE_RE.sub(" ", text or "")
    s = s.lower()
    s = s.replace("\\(", " ").replace("\\)", " ").replace("\\[", " ").replace("\\]", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _claim_in_rendered(claim: str, rendered_norm: str) -> bool:
    """Fuzzy containment: claim key content words appear in order in rendered text."""
    words = [w.strip(".,:;()[]\"'") for w in _normalize_for_binding(claim).split()]
    words = [w for w in words if len(w) > 3][:12]
    if not words:
        return True
    # Require first/last content words + majority in order (tolerates verdict-driven fixes)
    hits = sum(1 for w in words if w in rendered_norm)
    if words[0] not in rendered_norm or words[-1] not in rendered_norm:
        return False
    return hits / len(words) >= 0.6


def _rendered_matches_output(rendered: str, output: str) -> bool:
    """Rendered draft must substantially match the emitted message (90% char overlap)."""
    r, o = _normalize_for_binding(rendered), _normalize_for_binding(output)
    if not r:
        return False
    if r in o or o in r:
        return True
    # Overlap fallback: majority of rendered 5-grams present in output
    grams = [r[i : i + 24] for i in range(0, len(r), 24) if len(r[i : i + 24]) >= 12]
    if not grams:
        return r[:120] in o
    hits = sum(1 for g in grams if g in o)
    return hits / len(grams) >= 0.6


def _check_fact_check(data: dict, verd_text: str, content_str: str = ""):
    """Validate fact_check envelope + verdicts + generation-to-emission binding."""
    # Post-generation binding (2026-09): envelope must carry the actual draft text.
    rendered = data.get("rendered_content") or ""
    if not isinstance(rendered, str) or not rendered.strip():
        return (
            False,
            "MALFORMED_ENVELOPE",
            "GATE:fact_check requires rendered_content (actual draft step text). "
            "Draft the step internally, send it as rendered_content with claims[], "
            "fold verdicts, then emit the corrected final.",
        )
    # Lift per-claim source to top-level if needed (LLM drift)
    if not data.get("source_url") and not data.get("source_urls") and not data.get("source_file"):
        for c in (data.get("claims") or []):
            if isinstance(c, dict) and (c.get("source_url") or c.get("source_urls") or c.get("source_file")):
                if c.get("source_url"):
                    data["source_url"] = c.get("source_url")
                if c.get("source_urls"):
                    data["source_urls"] = c.get("source_urls")
                if c.get("source_file"):
                    data["source_file"] = c.get("source_file")
                break
    if GATEFactCheckEnvelope is not None:
        try:
            clean = dict(data)
            clean["claims"] = [{k: v for k, v in cc.items() if k in ("id", "claim")} if isinstance(cc, dict) else cc for cc in (clean.get("claims") or [])]
            GATEFactCheckEnvelope.model_validate(clean)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"fact_check envelope invalid: {e}"
    claims = data.get("claims") or []
    if not claims or not isinstance(claims, list):
        return False, "MALFORMED_ENVELOPE", "GATE:fact_check envelope missing claims[]"
    if not data.get("source_url") and not data.get("source_urls") and not data.get("source_file"):
        return False, "MALFORMED_ENVELOPE", "GATE:fact_check requires source_url(s) or source_file (multi-source source_urls preferred: Rohit + external refs)"
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdicts" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Subagent did not return {verdicts:[...]}"
    verdicts = verdict_data.get("verdicts") or []
    bad = [v for v in verdicts if v.get("verdict") not in ("PASS", "ISSUES", "UNVERIFIED")]
    if bad:
        return False, "MALFORMED_VERDICTS", f"Invalid verdict value: {bad[0].get('verdict')}"
    verdict_ids = {v.get("id") for v in verdicts}
    claim_ids = {c.get("id") for c in claims}
    if claim_ids - verdict_ids:
        return False, "MALFORMED_VERDICTS", f"Verdicts missing ids: {claim_ids - verdict_ids}"
    # Generation-to-emission binding: claims[] must appear in rendered_content,
    # and rendered_content must substantially match the emitted message.
    rendered_norm = _normalize_for_binding(rendered)
    for c in claims:
        claim_text = c.get("claim", "") if isinstance(c, dict) else str(c)
        if not _claim_in_rendered(claim_text, rendered_norm):
            return (
                False,
                "MALFORMED_ENVELOPE",
                f"Claim id={c.get('id') if isinstance(c, dict) else '?'} not found in "
                "rendered_content — send the actual draft text, not a plan summary.",
            )
    if content_str and not _rendered_matches_output(rendered, content_str):
        return (
            False,
            "MALFORMED_ENVELOPE",
            "rendered_content does not match the emitted message — the gate verifies "
            "what is generated, not what was planned. Redispatch with the actual draft.",
        )
    return True, "", ""


_BANNED_OPTION_RE = re.compile(r"\b(all|none)\s+of\s+the\s+above\b", re.I)


def _strip_option_label(text: str) -> str:
    """Remove leading A-D/1-4 labels, pipes, and bold markers from a rendered option."""
    s = re.sub(r"^[\s\|\-\*\>]*\(?[A-Da-d1-4]\)?[\.\)\:\|\-]\s*", "", (text or "").strip())
    return s.replace("**", "").strip()


def _is_code_option(options) -> bool:
    """Code/math options get natural length variance — exempt from length pattern."""
    blob = " ".join(str(o) for o in (options or []))
    return ("```" in blob) or ("\\(" in blob) or ("\\[" in blob)


def _option_lens(options) -> list:
    lens = []
    for o in (options or []):
        s = _strip_option_label(str(o))
        s = re.sub(r"```.*?```", "CODE", s, flags=re.DOTALL)
        lens.append(len(s.strip()))
    return lens


def _check_quiz_audit(data: dict, verd_text: str, content_str: str = ""):
    if GATEQuizAuditEnvelope is not None:
        try:
            GATEQuizAuditEnvelope.model_validate(data)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"quiz_audit envelope invalid: {e}"
    if not data.get("questions_json") or not isinstance(data.get("questions_json"), list):
        return False, "MALFORMED_ENVELOPE", "GATE:quiz_audit requires questions_json[]"
    # Deterministic per-item structural checks (Pipe-side: schema import may fail open)
    mcqs = []
    for q in (data.get("questions_json") or []):
        if not isinstance(q, dict):
            return False, "MALFORMED_ENVELOPE", "GATE:quiz_audit questions_json[] items must be objects"
        qid = q.get("id", "?")
        qtype = q.get("type", "mcq")
        if qtype == "mcq":
            opts = q.get("options")
            ci = q.get("correct_index")
            if not isinstance(opts, list) or len(opts) != 4:
                return False, "MALFORMED_ENVELOPE", f"Quiz item {qid}: MCQ requires exactly 4 options"
            if not isinstance(ci, int) or not 0 <= ci < 4:
                return False, "MALFORMED_ENVELOPE", f"Quiz item {qid}: correct_index out of range"
            for o in opts:
                if _BANNED_OPTION_RE.search(str(o)):
                    return (
                        False,
                        "MALFORMED_ENVELOPE",
                        f"Quiz item {qid}: 'all/none of the above' is banned — rewrite options "
                        "as four parallel, topically-plausible alternatives.",
                    )
            mcqs.append(q)
    # Batch-pattern blocks (tolerant: batches <3 leave variety to the auditor)
    if len(mcqs) >= 3:
        slots = [q.get("correct_index") for q in mcqs]
        if len(set(slots)) == 1:
            return (
                False,
                "MALFORMED_ENVELOPE",
                "Quiz batch: correct answer sits in the same slot every time — "
                "randomize correct positions across questions.",
            )
        eligible = [q for q in mcqs if not _is_code_option(q.get("options"))]
        if len(eligible) >= 3:
            flagged = []
            for q in eligible:
                lens = _option_lens(q.get("options"))
                med = sorted(lens)[len(lens) // 2] or 1
                ci_len = lens[q.get("correct_index")]
                if (ci_len == max(lens) and ci_len > 1.25 * med) or (
                    ci_len == min(lens) and ci_len < 0.75 * med
                ):
                    flagged.append(str(q.get("id", "?")))
            if flagged and len(flagged) / len(eligible) >= 2 / 3:
                return (
                    False,
                    "MALFORMED_ENVELOPE",
                    f"Quiz items {flagged}: correct option is the length outlier "
                    "(longest/shortest) across the batch — balance option lengths so "
                    "the answer can't be spotted by shape.",
                )
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdict" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Quiz-audit subagent did not return {verdict: PASS|ISSUES}"
    if verdict_data.get("verdict") not in ("PASS", "ISSUES"):
        return False, "MALFORMED_VERDICTS", f"Invalid quiz verdict: {verdict_data.get('verdict')}"
    # Generation-to-emission binding: verified batch must match the emitted message.
    if content_str:
        out_norm = _normalize_for_binding(content_str)
        for q in (data.get("questions_json") or []):
            if not isinstance(q, dict):
                continue
            qid = q.get("id", "?")
            if not _claim_in_rendered(str(q.get("question", "")), out_norm):
                return (
                    False,
                    "MALFORMED_ENVELOPE",
                    f"Quiz item {qid}: verified question not found in the emitted message — "
                    "the gate audits what is rendered, not what was planned. "
                    "Redispatch with the actual batch.",
                )
            if (q.get("type", "mcq")) == "mcq":
                hits = sum(
                    1
                    for o in (q.get("options") or [])
                    if _claim_in_rendered(_strip_option_label(str(o)), out_norm)
                )
                if hits < 3:
                    return (
                        False,
                        "MALFORMED_ENVELOPE",
                        f"Quiz item {qid}: verified options not found in the emitted message — "
                        "redispatch with the actual batch.",
                    )
    return True, "", ""


def _check_grade_audit(data: dict, verd_text: str):
    if GATEGradeAuditEnvelope is not None:
        try:
            GATEGradeAuditEnvelope.model_validate(data)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"grade_audit envelope invalid: {e}"
    for field in ("concept", "question", "learner_answer", "claimed_verdict", "source_excerpt"):
        if not data.get(field):
            return False, "MALFORMED_ENVELOPE", f"GATE:grade_audit requires {field}"
    if data.get("claimed_verdict") not in ("pass", "fail"):
        return False, "MALFORMED_ENVELOPE", "GATE:grade_audit claimed_verdict must be pass|fail"
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdict" not in verdict_data or "correct_verdict" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Grade-audit subagent did not return {verdict: PASS|ISSUES, agrees, correct_verdict}"
    if verdict_data.get("verdict") not in ("PASS", "ISSUES"):
        return False, "MALFORMED_VERDICTS", f"Invalid grade verdict: {verdict_data.get('verdict')}"
    if verdict_data.get("correct_verdict") not in ("pass", "fail"):
        return False, "MALFORMED_VERDICTS", "correct_verdict must be pass|fail"
    return True, "", ""


def _resolve_wiki_files(concepts, repo_root: str) -> dict:
    """Map each concept to candidate wiki files. Returns {concept: [Path]}."""
    wiki_dir = Path(repo_root) / "Knowledge Wiki" / "wiki"
    mapping: dict = {}
    if not wiki_dir.exists():
        return mapping
    pages = list(wiki_dir.glob("*.md"))
    for concept in (concepts or []):
        cslug = _slugify(str(concept))
        hits = [p for p in pages if cslug and (cslug in _slugify(p.stem) or _slugify(p.stem) in cslug)]
        mapping[str(concept)] = hits
    return mapping


def _wiki_matches_files(wiki_content: str, files) -> float:
    """Fraction of substantial wiki_content paragraphs found verbatim in files."""
    blocks = [b for b in re.split(r"\n\s*\n", wiki_content or "") if len(_normalize_for_binding(b)) >= 40]
    if not blocks:
        return 1.0
    combined = _normalize_for_binding(" ".join(p.read_text(encoding="utf-8", errors="replace") for p in files))
    if not combined:
        return 0.0
    hits = sum(1 for b in blocks if _normalize_for_binding(b) in combined)
    return hits / len(blocks)


def _check_review(data: dict, verd_text: str, content_str: str = "", repo_root: str = ""):
    if GATEReviewEnvelope is not None:
        try:
            GATEReviewEnvelope.model_validate(data)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"review envelope invalid: {e}"
    if not data.get("wiki_content") or not data.get("concepts"):
        return False, "MALFORMED_ENVELOPE", "GATE:review requires wiki_content and concepts"
    if not data.get("source_url") and not data.get("source_file") and not data.get("lesson_ref"):
        return (
            False,
            "MALFORMED_ENVELOPE",
            "GATE:review requires grounding: source_url, source_file, or lesson_ref "
            "(the reviewer verifies against the source, not from memory).",
        )
    wiki_norm = _normalize_for_binding(str(data.get("wiki_content") or ""))
    for concept in (data.get("concepts") or []):
        if not _claim_in_rendered(str(concept), wiki_norm):
            return (
                False,
                "MALFORMED_ENVELOPE",
                f"Concept '{concept}' not found in wiki_content — send the actual "
                "written content, not a summary.",
            )
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdict" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Review subagent did not return {verdict: PASS|ISSUES}"
    if verdict_data.get("verdict") not in ("PASS", "ISSUES"):
        return False, "MALFORMED_VERDICTS", f"Invalid review verdict: {verdict_data.get('verdict')}"
    # Generation-to-emission binding (file-grounded): the reviewed wiki_content must
    # match what was actually written. The final message is a summary, so message
    # containment would false-positive — compare against files on disk instead.
    # Files are written via ops.py apply before the final message, so at outlet
    # time the artifact exists. Fail open when the repo is unreachable.
    if repo_root:
        mapping = _resolve_wiki_files(data.get("concepts"), repo_root)
        if mapping:
            missing = [c for c, files in mapping.items() if not files]
            if missing:
                return (
                    False,
                    "MALFORMED_ENVELOPE",
                    f"No wiki file found for concept(s) {missing} — write the pages "
                    "before dispatching review.",
                )
            all_files = [p for files in mapping.values() for p in files]
            overlap = _wiki_matches_files(str(data.get("wiki_content") or ""), all_files)
            if overlap < 0.6:
                return (
                    False,
                    "MALFORMED_ENVELOPE",
                    "Written wiki files do not match the reviewed wiki_content — the gate "
                    "reviews what was written, not what was planned. Redispatch with "
                    "the actual written content.",
                )
    return True, "", ""


def _check_review_session(data: dict, verd_text: str, content_str: str = "", repo_root: str = ""):
    """Validate GATE:review_session envelope + verdicts + written-file grounding.

    The reviewer audits the Clerk's end-of-review writes (Review notes, session
    note, touched state rows) against the session transcript and the per-grade
    verdicts. Scope is fenced: state drift the review did not write is the state
    audit's job, never a blocking issue here.
    """
    if GATEReviewSessionEnvelope is not None:
        try:
            GATEReviewSessionEnvelope.model_validate(data)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"review_session envelope invalid: {e}"
    if not data.get("concepts"):
        return False, "MALFORMED_ENVELOPE", "GATE:review_session requires concepts[]"
    if not data.get("transcript"):
        return False, "MALFORMED_ENVELOPE", "GATE:review_session requires transcript (exact Q/A + verdicts)"
    files = data.get("written_files")
    if not files or not isinstance(files, list):
        return False, "MALFORMED_ENVELOPE", "GATE:review_session requires written_files[]"
    for f in files:
        if not isinstance(f, dict) or not f.get("path") or not f.get("content"):
            return False, "MALFORMED_ENVELOPE", "review_session written_files[] items need path and content"
    # File grounding (generation-to-emission): the reviewed artifacts must match
    # the files actually written. Files land via ops.py apply before the final
    # message, so at outlet time they exist. Fail open when the repo is unreachable.
    if repo_root:
        missing, mismatch = [], []
        for f in files:
            p = Path(repo_root) / str(f.get("path"))
            if not p.exists():
                missing.append(str(f.get("path")))
                continue
            overlap = _wiki_matches_files(str(f.get("content") or ""), [p])
            if overlap < 0.6:
                mismatch.append(str(f.get("path")))
        if missing:
            return (
                False,
                "MALFORMED_ENVELOPE",
                f"review_session: written file(s) not found on disk: {missing} — write them "
                "before dispatching the audit.",
            )
        if mismatch:
            return (
                False,
                "MALFORMED_ENVELOPE",
                f"review_session: written file(s) do not match the audited content: {mismatch} — "
                "the audit reviews what was written, not what was planned.",
            )
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdict" not in verdict_data:
        return (
            False,
            "MALFORMED_VERDICTS",
            "Review-session audit did not return {verdict: PASS|PASS_WITH_FLAGS|ISSUES}",
        )
    if verdict_data.get("verdict") not in ("PASS", "PASS_WITH_FLAGS", "ISSUES"):
        return False, "MALFORMED_VERDICTS", f"Invalid review_session verdict: {verdict_data.get('verdict')}"
    return True, "", ""


def _review_session_flagged(verd_text: str) -> bool:
    """True when the review-session audit returned ISSUES (banner + render)."""
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    return bool(verdict_data and verdict_data.get("verdict") == "ISSUES")


def _parse_gate_envelope(task: str):
    """Extract gate data dict from delegate_task payload, handling GATE: prefix."""
    json_part = task
    if "GATE:" in task:
        parts = task.split("\n", 1)
        if len(parts) == 2:
            json_part = parts[1]
    stripped = json_part.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except Exception:
            return extract_json_block(task) if callable(extract_json_block) else None
    return extract_json_block(task) if callable(extract_json_block) else None


def _slugify(text: str) -> str:
    s = SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return s[:64] or "lesson"


def _extract_topic(parent_text: str) -> str:
    """Extract topic from trigger text — first line only, strip template boilerplate."""
    if not parent_text:
        return ""
    first_line = parent_text.strip().split("\n", 1)[0]
    # Try "teach me X" / "/teach X" pattern on first line only
    m = re.search(r"(?:/teach|teach me)\s+(.+)", first_line, re.I)
    if m:
        topic = m.group(1).strip()
        # Strip trailing boilerplate like "Load the learning-teach skill"
        topic = re.split(r"\s+Load the\b", topic, flags=re.I)[0].strip()
        # Strip leading "about:" that appears in "Teach me about: X" prompts
        topic = re.sub(r"^\s*about\s*:\s*", "", topic, flags=re.I)
        topic = topic.strip("\"' :")
        return topic
    # For /lesson, topic is not in trigger — use curriculum lookup; return empty
    # For bare triggers, return first line truncated
    return first_line[:120]


def _is_scout_message(msg: dict, valves) -> bool:
    prefix = getattr(valves, "scout_name_prefix", "Scout")
    model = msg.get("model") or ""
    models = msg.get("models")
    if isinstance(models, list) and models:
        # models is list of model ids for this message
        if any(prefix.lower() in str(m).lower() for m in models):
            return True
    if model and prefix.lower() in str(model).lower():
        return True
    # Content marker fallback
    content = msg.get("content") or ""
    if isinstance(content, list):
        content = "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
    return "SCOUT DIGEST" in str(content)


def _is_tutor_preset(model_id: str, valves) -> bool:
    prefix = getattr(valves, "tutor_name_prefix", "Tutor")
    return prefix.lower() in (model_id or "").lower()


def _is_clerk_preset(model_id: str, valves) -> bool:
    prefix = getattr(valves, "clerk_name_prefix", "Clerk")
    return prefix.lower() in (model_id or "").lower()


def _is_deputy_preset(model_id: str, valves) -> bool:
    """User's review preset: held to the same clerk-role rules as Clerk."""
    prefix = getattr(valves, "deputy_name_prefix", "Deputy")
    return bool(prefix) and prefix.lower() in (model_id or "").lower()


def _find_digest(chat_id: str, slug: str, ttl_days: int, repo_root: str):
    base = Path(repo_root) / "Learning System" / TMP_DIR
    if not base.exists():
        return None
    # Prefer exact slug match
    exact = list(base.glob(f"context-{chat_id}-{slug}.json"))
    candidates = exact if exact else list(base.glob(f"context-{chat_id}-*.json"))
    # Fallback: legacy Scout files without chat_id prefix (e.g. context-mission-0-*.json)
    # and generic slug mismatches like "next-lesson" vs digest slug "mission-0-catchup-foundations"
    if not candidates:
        candidates = list(base.glob("context-*.json"))
        # For alias topics like "next-lesson", "lesson", "continue" — prefer the newest
        # digest for this chat if any, otherwise any recent digest
        if slug in ("next-lesson", "lesson", "continue", "gather-context-for-next-lesson"):
            chat_candidates = list(base.glob(f"context-{chat_id}-*.json"))
            if chat_candidates:
                candidates = chat_candidates
    # Filter by TTL and pick newest
    valid = []
    for p in candidates:
        try:
            age_days = (time.time() - p.stat().st_mtime) / 86400
            if age_days > ttl_days:
                continue
            # For exact match, verify; for fallback, accept any recent digest for this chat
            valid.append(p)
        except Exception:
            continue
    if not valid:
        return None
    # Newest first
    valid.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    # Alias slugs should accept any recent digest (return newest)
    if slug in ("next-lesson", "lesson", "continue", "gather-context-for-next-lesson"):
        return valid[0]
    # If we used fallback, return newest regardless of slug
    if exact:
        for p in valid:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("slug") == slug:
                    return p
            except Exception:
                continue
        # Exact glob matched but slug field mismatched — still return newest exact
        return valid[0]
    # No exact match — check if any candidate's internal slug matches requested slug
    for p in valid:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("slug") == slug:
                return p
        except Exception:
            continue
    return valid[0]


def _sweep_expired(repo_root: str, ttl_days: int):
    base = Path(repo_root) / "Learning System" / TMP_DIR
    if not base.exists():
        return
    now = time.time()
    for p in base.glob("context-*.json"):
        try:
            if (now - p.stat().st_mtime) / 86400 > ttl_days:
                p.unlink()
        except Exception:
            pass


def _get_repo_root(valves, body: dict) -> str:
    # Valve override takes precedence
    v_root = getattr(valves, "repo_root", "") if valves else ""
    if v_root and os.path.isdir(v_root):
        return v_root
    for cand in [
        "/home/user/learning-system",
        "/home/delinux/learning-system",
        os.path.expanduser("~/learning-system"),
    ]:
        if os.path.isdir(cand):
            return cand
    return os.path.expanduser("~/learning-system")


def _last_user_message(hist: dict):
    """Return (msg_id, text) of the most recent user message in history."""
    if not hist:
        return None, ""
    # hist is dict of id -> msg
    # Find max timestamp user message
    user_msgs = [m for m in hist.values() if m.get("role") == "user"]
    if not user_msgs:
        return None, ""
    # Prefer latest timestamp; fallback to insertion order
    try:
        latest = max(user_msgs, key=lambda m: m.get("timestamp", 0))
    except Exception:
        latest = user_msgs[-1]
    mid = latest.get("id")
    content = latest.get("content") or ""
    if isinstance(content, list):
        content = "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
    return mid, str(content)


class Filter:
    class Valves(BaseModel):  # type: ignore
        priority: int = Field(default=10, description="Filter priority (higher runs later)")
        max_retries: int = Field(default=2, ge=0, le=5, description="Max fix retries per user turn")
        digest_ttl_days: int = Field(default=7, ge=1, le=30)
        scout_name_prefix: str = Field(default="Scout")
        tutor_name_prefix: str = Field(default="Tutor")
        clerk_name_prefix: str = Field(default="Clerk")
        deputy_name_prefix: str = Field(default="Deputy", description="User's review preset — held to clerk-role rules (empty disables)")
        repo_root: str = Field(default="", description="Override repo path (empty = auto-detect)")
        blocked_banner: str = Field(
            default="⛔ Withheld: not independently verified — retry limit reached. Fix the GATE envelope and retry.",
            description="Banner shown after retry cap",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def inlet(self, body: dict, __user__: dict = None, __request__=None, __metadata__: dict = None) -> dict:  # type: ignore
        try:
            repo_root = _get_repo_root(self.valves, body)
            _sweep_expired(repo_root, getattr(self.valves, "digest_ttl_days", 7))
        except Exception:
            pass
        return body

    def _parse_child_hist(self, hist: dict):
        task = ""
        content = ""
        for m in (hist or {}).values():
            if m.get("role") == "user":
                task = m.get("content") or task
            if m.get("role") == "assistant":
                content = m.get("content") or content
        is_done = any(isinstance(v, dict) and v.get("done") for v in (hist or {}).values())
        return task, content, is_done

    async def _fetch_child_chats(self, chat_id: str, assistant_id: str, user: dict):
        """Fetch foreground subagent receipts with parent_message_id == assistant_id."""
        child_chats: list[dict] = []
        try:
            from sqlalchemy import select
            from open_webui.internal.db import get_async_db
            from open_webui.models.chats import Chat

            user_id = user.get("id")
            async with get_async_db() as db:
                result = await db.execute(
                    select(Chat).where(
                        Chat.user_id == user_id,
                        Chat.meta["internal"].as_boolean().is_(True),
                        Chat.meta["type"].as_string() == "subagent",
                        Chat.meta["parent_message_id"].as_string() == assistant_id,
                    )
                )
                for row in result.scalars().all():
                    meta = row.meta or {}
                    hist = (row.chat or {}).get("history", {}).get("messages", {}) if hasattr(row, "chat") else {}
                    task, content, is_done = self._parse_child_hist(hist)
                    child_chats.append(
                        {"id": row.id, "meta": meta, "mode": meta.get("mode", ""), "task": task, "content": content, "done": is_done}
                    )
            if child_chats:
                return child_chats

            # Fallback: legacy lookup via parent chat id
            from open_webui.models.chats import Chats

            ids = await Chats.get_internal_chat_ids_by_parent_id(chat_id, user_id)
            for cid in ids:
                c = await Chats.get_chat_by_id(cid)
                if not c or (c.meta or {}).get("parent_message_id") != assistant_id:
                    continue
                meta = c.meta or {}
                if (meta.get("mode") or "").lower() in ("background", "async"):
                    continue
                hist = (c.chat or {}).get("history", {}).get("messages", {})
                task, content, is_done = self._parse_child_hist(hist)
                if not is_done:
                    continue
                child_chats.append({"id": cid, "meta": meta, "mode": meta.get("mode", ""), "task": task, "content": content, "done": True})
        except Exception as e:
            try:
                import logging

                logging.getLogger(__name__).warning(f"gate_pipe child lookup failed (fail open): {e}")
            except Exception:
                pass
            return None  # signal fail-open to caller
        return child_chats

    async def outlet(self, body: dict, __user__: dict = None, __request__=None, __metadata__: dict = None, __model__: dict = None) -> dict:  # type: ignore
        """
        body shape (middleware outlet_filter_handler):
          {model, messages: [{id, role, content, ...}], chat_id, id (assistant message id), filter_ids}
        Returns modified body; content replacement is persisted and emitted via chat:outlet.
        """
        try:
            valves = self.valves
            model_id = body.get("model") or (__model__.get("id") if isinstance(__model__, dict) else "") or ""
            chat_id = body.get("chat_id") or (__metadata__ or {}).get("chat_id") or ""
            assistant_id = body.get("id") or ""
            messages = body.get("messages") or []
            if not messages:
                return body

            # Exempt internal subagent chats (verifiers) — they are not Tutor/Clerk teaching
            # and must not be recursively gated. This prevents verifier BLOCKED loops.
            try:
                if chat_id and __user__ and __user__.get("id"):
                    from open_webui.models.chats import Chats as _ChatsExempt

                    _c = await _ChatsExempt.get_chat_by_id_and_user_id(chat_id, __user__.get("id"))
                    if _c and (_c.meta or {}).get("internal") is True:
                        return body
                    # Also exempt if body came from a subagent invocation (internal parent)
                    if _c and (_c.meta or {}).get("type") == "subagent":
                        return body
            except Exception:
                pass

            is_tutor = _is_tutor_preset(model_id, valves)
            is_clerk = _is_clerk_preset(model_id, valves) or _is_deputy_preset(model_id, valves)
            if not is_tutor and not is_clerk:
                scout_prefix = getattr(valves, "scout_name_prefix", "Scout").lower()
                if scout_prefix in (model_id or "").lower():
                    return body
                return body

            repo_root = _get_repo_root(valves, body)
            assistant_msg = None
            for m in messages:
                if m.get("id") == assistant_id:
                    assistant_msg = m
                    break
            if not assistant_msg and messages:
                assistant_msg = messages[-1]
                assistant_id = assistant_msg.get("id") or assistant_id

            content = assistant_msg.get("content") or ""
            if isinstance(content, list):
                content = "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
            content_str = str(content)

            # If no request/DB available, fail open (don't block unsaved/temp chats)
            if __request__ is None or not chat_id or not __user__ or not __user__.get("id"):
                return body

            # Fetch full chat history from DB
            chat_history = {}
            parent_user_id = None
            parent_user_text = ""
            try:
                from open_webui.models.chats import Chats

                chat = await Chats.get_chat_by_id_and_user_id(chat_id, __user__.get("id"))
                if chat and getattr(chat, "chat", None):
                    hist = (chat.chat or {}).get("history", {}).get("messages", {}) or {}
                    chat_history = hist
                    parent_user_id, parent_user_text = _last_user_message(hist)
            except Exception as e:
                # Fail open on DB error — but log at WARNING so the gap is
                # visible in `docker logs open-webui` (do not silently pass).
                try:
                    import logging

                    logging.getLogger(__name__).warning(f"gate_pipe DB history fetch failed (fail open): {e}")
                except Exception:
                    pass
                return body

            # Turn-scoped retry state: reset if this is a new user turn
            try:
                from open_webui.models.chats import Chats as _Chats2

                chat_for_state = await _Chats2.get_chat_by_id_and_user_id(chat_id, __user__.get("id"))
                if chat_for_state:
                    state = (chat_for_state.meta or {}).get("gate_state") or {}
                    last_uid = state.get("last_user_msg_id")
                    if parent_user_id and last_uid and parent_user_id != last_uid:
                        # New turn — reset retries
                        await self._reset_gate_state(chat_id, __user__, __request__)
            except Exception:
                pass

            # Decide if this is a new-lesson trigger vs resume
            is_new_lesson_trigger = bool(TRIGGER_RE.search(parent_user_text or ""))
            # Derive slug from topic (first line) for digest lookup
            topic = _extract_topic(parent_user_text)
            slug = _slugify(topic) if topic else _slugify(parent_user_text)

            has_lesson_file = False
            if slug and slug != "lesson":
                lessons_dir = Path(repo_root) / "Learning System" / "Lessons"
                if lessons_dir.exists():
                    for p in lessons_dir.glob("*.md"):
                        if slug in _slugify(p.stem):
                            has_lesson_file = True
                            break
            else:
                # Empty/generic slug — check if any lesson exists for this chat's recent topic is unreliable;
                # treat as no lesson file so digest check can proceed via fallback
                has_lesson_file = False

            # Gate 1: Scout digest required only for new-lesson Tutor turns
            if is_tutor and is_new_lesson_trigger and not has_lesson_file:
                digest = _find_digest(chat_id, slug, getattr(valves, "digest_ttl_days", 7), repo_root)
                has_scout_msg = any(_is_scout_message(m, valves) for m in chat_history.values())
                # If repo filesystem is not mounted in Open WebUI (common: /home/user is in
                # open-terminal volume, not open-webui), digest will be None even when Scout
                # succeeded. In that case, rely on SCOUT DIGEST message alone (graceful degrade)
                # rather than permanently blocking new lessons.
                digest_base = Path(repo_root) / "Learning System" / TMP_DIR
                repo_unavailable = not digest_base.exists()
                if repo_unavailable and has_scout_msg:
                    # Fail open for file part — message proves Scout ran
                    pass
                elif not digest or not has_scout_msg:
                    blocked = (
                        f"⛔ BLOCKED (NO_SCOUT_CONTEXT) — No Scout digest found for this lesson (`{slug}`).\n\n"
                        f"Switch to your **{getattr(valves, 'scout_name_prefix', 'Scout')}** preset in this same chat and gather context for: `{parent_user_text[:120]}`.\n"
                        f"Then switch back to **{getattr(valves, 'tutor_name_prefix', 'Tutor')}** and retry. "
                        f"Digest expected at `Learning System/.tmp/context-{chat_id}-{slug}.json` (7-day TTL)."
                    )
                    should_retry, cap_msg = await self._check_retry_cap(chat_id, __user__, __request__, parent_user_id)
                    if not should_retry:
                        blocked = cap_msg or getattr(valves, "blocked_banner", "⛔ Withheld: not independently verified.")
                    else:
                        # Record this attempt against the current user turn
                        await self._bump_gate_state(chat_id, __user__, __request__, "NO_SCOUT_CONTEXT", parent_user_id)
                    assistant_msg["content"] = blocked
                    return body

            # Gate 2: Per-generation receipts — Tutor is multi-turn; Clerk single-turn
            needs_fact_check, needs_quiz_audit, needs_review, needs_grade, needs_review_session = _gate_needs(
                content_str, is_tutor, is_clerk
            )
            needs_receipt = any(
                (needs_fact_check, needs_quiz_audit, needs_review, needs_grade, needs_review_session)
            )

            if not needs_receipt:
                # Trivial messages don't need receipts, but don't reset turn-scoped cap here
                # (that would allow gaming via short acks). Only valid receipts reset.
                return body

            child_chats = await self._fetch_child_chats(chat_id, assistant_id, __user__)
            if child_chats is None:
                return body  # fail open on DB error (helper already logged)

            # Validate receipts per role — Tutor is per-generation (fix 2026-09-01):
            # each Tutor message that contains claims must have a fresh fact_check,
            # each that contains a quiz must have a fresh quiz_audit. An upfront
            # Plan batch never covers later steps, and quiz_audit never covers claims.
            found_fact_check = False
            found_quiz_audit = False
            found_review = False
            found_grade_audit = False
            found_review_session = False
            review_session_issues = False
            reject_code = "NO_DELEGATION"
            reject_detail = "No foreground GATE envelope dispatched via delegate_task for this generation. Each Tutor step needs its own fresh receipt (parent_message_id == this message)."

            if child_chats:
                for ch in child_chats:
                    # Foreground check via meta.mode (authoritative) + done flag
                    mode = (ch.get("mode") or "").lower()
                    is_background = mode == "background" or mode == "async"
                    if is_background or not ch.get("done"):
                        # Background or not yet done — not a valid receipt for this gate
                        reject_code = "MALFORMED_ENVELOPE"
                        reject_detail = "Gate must be foreground (background:false) and completed before presenting. Retry with foreground delegate_task."
                        continue

                    task = ch.get("task") or ""
                    verd_text = ch.get("content") or ""
                    data = _parse_gate_envelope(task)
                    if not data or not isinstance(data, dict) or "gate" not in data:
                        reject_code = "MALFORMED_ENVELOPE"
                        reject_detail = "GATE envelope must be JSON with gate field (fact_check | review | review_session | quiz_audit | grade_audit)"
                        continue
                    gate_type = data.get("gate")

                    if gate_type == "fact_check" and is_tutor:
                        ok, code, detail = _check_fact_check(data, verd_text, content_str)
                        if ok:
                            found_fact_check = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    if gate_type == "quiz_audit" and is_tutor:
                        ok, code, detail = _check_quiz_audit(data, verd_text, content_str)
                        if ok:
                            found_quiz_audit = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    if gate_type == "review" and is_clerk:
                        ok, code, detail = _check_review(data, verd_text, content_str, repo_root)
                        if ok:
                            found_review = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    if gate_type == "review_session" and (is_clerk or is_tutor):
                        ok, code, detail = _check_review_session(data, verd_text, content_str, repo_root)
                        if ok:
                            found_review_session = True
                            if _review_session_flagged(verd_text):
                                review_session_issues = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    if gate_type == "grade_audit" and (is_tutor or is_clerk):
                        ok, code, detail = _check_grade_audit(data, verd_text)
                        if ok:
                            found_grade_audit = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    # Cross-role envelope: e.g., quiz_audit on Clerk — treat as invalid gate for that role
                    reject_code = "MALFORMED_ENVELOPE"
                    reject_detail = f"Gate type '{gate_type}' not valid for this preset ({model_id})"
                    continue

            # Evaluate per-generation requirement (Tutor only)
            if is_tutor:
                # Review-session close: audit the end-of-review writes. On ISSUES
                # after the fix loop the receipt is still valid — banner + render,
                # never withhold (the pi dead-end lesson).
                if needs_review_session:
                    if found_review_session:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        if review_session_issues:
                            assistant_msg["content"] = _REVIEW_SESSION_FLAGS_BANNER + content_str
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Review-session close requires a foreground GATE:review_session receipt for THIS generation — the end-of-review writes (Review notes, session note, touched state rows) must be audited against the transcript and grade verdicts. Dispatch review_session before presenting the summary."
                # Review grading: strict — grade must carry a fresh grade_audit.
                elif needs_grade:
                    if found_grade_audit:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Review grade requires a foreground GATE:grade_audit receipt for THIS generation (parent_message_id == this message). Dispatch grade_audit with concept/question/learner_answer/claimed_verdict/source_excerpt before presenting the grade."
                # Tutor: each generation needs fresh receipt matching its content type.
                # Mixed claims+quiz needs BOTH. Upfront Plan batch never covers later steps.
                elif needs_fact_check and needs_quiz_audit:
                    if found_fact_check and found_quiz_audit:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    if not found_fact_check and not found_quiz_audit:
                        reject_code = "NO_DELEGATION"
                        reject_detail = "Mixed claims+quiz message requires BOTH fact_check and quiz_audit receipts for this generation (parent_message_id == this message). Dispatch both foreground GATE envelopes before presenting."
                    elif not found_fact_check:
                        reject_code = "NO_DELEGATION"
                        reject_detail = "Per-generation fact_check required before this teaching step (mixed message). Dispatch a foreground GATE:fact_check for the claims in THIS generation. Upfront Plan verification does not cover Teach steps, and quiz_audit does not cover claims."
                    else:  # found_fact_check but not found_quiz_audit
                        reject_code = "NO_DELEGATION"
                        reject_detail = "Quiz part of this mixed message requires GATE:quiz_audit receipt for this generation (parent_message_id == this message)."
                elif needs_fact_check:
                    if found_fact_check:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Per-generation fact_check required before this teaching step. Dispatch a foreground GATE:fact_check for the claims you are about to present in THIS generation (parent_message_id == this message). Upfront Plan verification does not cover Teach steps, and quiz_audit does not cover claims."
                elif needs_quiz_audit:
                    if found_quiz_audit:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Quiz batch requires GATE:quiz_audit receipt for this generation (parent_message_id == this message). Dispatch foreground quiz_audit before presenting questions."
                else:
                    # Non-trivial but heuristics missed — treat as needs fact_check
                    pass
            elif is_clerk:
                # Clerk review sessions: a session close needs review_session,
                # grade turns need grade_audit, wiki writes need review.
                if needs_review_session:
                    if found_review_session:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        if review_session_issues:
                            assistant_msg["content"] = _REVIEW_SESSION_FLAGS_BANNER + content_str
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Review-session close requires a foreground GATE:review_session receipt for THIS generation — the end-of-review writes (Review notes, session note, touched state rows) must be audited against the transcript and grade verdicts. Dispatch review_session before presenting the summary."
                elif needs_grade:
                    if found_grade_audit:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Review grade requires a foreground GATE:grade_audit receipt for THIS generation (parent_message_id == this message). Dispatch grade_audit with concept/question/learner_answer/claimed_verdict/source_excerpt before presenting the grade."
                elif found_review:
                    await self._reset_gate_state(chat_id, __user__, __request__)
                    return body
            else:
                # Should not reach here (Scout exempt)
                return body

            # No valid receipt — check cap and block
            should_retry, cap_msg = await self._check_retry_cap(chat_id, __user__, __request__, parent_user_id)
            if not should_retry:
                assistant_msg["content"] = cap_msg or getattr(valves, "blocked_banner", "⛔ Withheld: not independently verified.")
                return body

            if needs_review_session:
                detail_help = (
                    f"⛔ BLOCKED ({reject_code}) — {reject_detail}\n\n"
                    f"Dispatch a foreground GATE:review_session envelope via delegate_task on the exact session "
                    f"writes (generation-to-emission: write the notes/rows first, audit what was written, then summarize):\n"
                    f"```json\n"
                    f'{{\n  "gate": "review_session",\n  "concepts": ["Concept"],\n'
                    f'  "transcript": "exact Q/A + learner answers + claimed verdicts",\n'
                    f'  "grade_verdicts": [{{"concept": "Concept", "correct_verdict": "pass"}}],\n'
                    f'  "written_files": [{{"path": "Learning System/Reviews/Review — Concept — YYYY-MM-DD.md", "content": "exact written text"}}],\n'
                    f'  "state_rows": "exact touched Active Concepts / Mistakes / Attempts text"\n}}\n```\n'
                    f"The written files must exist and match the audited content; scope is fenced — state drift the "
                    f"review did not write is context_notes, never a blocking issue."
                )
            elif is_tutor:
                detail_help = (
                    f"⛔ BLOCKED ({reject_code}) — {reject_detail}\n\n"
                    f"Learning Tutor is multi-turn: **each generation** needs its own fresh GATE receipt before you emit it (parent_message_id must equal this message's id). Do NOT reuse an upfront Plan batch for later Teach steps.\n\n"
                    f"For teaching claims in THIS step (generation-to-emission: draft internally, verify draft, then emit):\n"
                    f"```json\n"
                    f'{{\n  "gate": "fact_check",\n  "claims": [{{"id": 1, "claim": "load-bearing claim for THIS step"}}],\n'
                    f'  "rendered_content": "actual draft step text that will be emitted (pre-corrections)",\n'
                    f'  "source_urls": ["https://rohit-source...", "https://external-ref..."],\n'
                    f'  "reference_excerpt": "digest excerpts for THIS step",\n'
                    f'  "context": "what THIS step teaches"\n}}\n```\n'
                    f"For question batches in THIS generation (verified batch must equal rendered batch):\n"
                    f"```json\n"
                    f'{{\n  "gate": "quiz_audit",\n  "questions_json": [{{"id":"q1","type":"mcq","question":"...","options":["a","b","c","d"],"correct_index":1,"target_bloom":"Apply"}}],\n'
                    f'  "purpose": "probe", "concept": "Concept", "source_excerpt": "..."\n}}\n```\n'
                    f"Quiz rules enforced deterministically: 4 options + correct_index in range per MCQ; "
                    f"no 'all/none of the above'; batches of 3+ must vary correct positions and must not "
                    f"make the correct option the length outlier across the batch.\n"
                    f"For review grades in THIS generation:\n"
                    f"```json\n"
                    f'{{\n  "gate": "grade_audit",\n  "concept": "Concept",\n  "question": "what was asked",\n  "learner_answer": "raw answer",\n  "claimed_verdict": "pass",\n  "source_excerpt": "Concept Note / Lesson / Wiki excerpt"\n}}\n```\n'
                    f"Mixed claims+quiz needs BOTH receipts for the same message. Subagent prompt is fixed via global subagents.system_prompt — send data only."
                )
            elif is_clerk and needs_grade:
                detail_help = (
                    f"⛔ BLOCKED ({reject_code}) — {reject_detail}\n\n"
                    f"Dispatch a foreground GATE:grade_audit envelope via delegate_task before presenting the grade:\n"
                    f"```json\n"
                    f'{{\n  "gate": "grade_audit",\n  "concept": "Concept",\n  "question": "what was asked",\n  "learner_answer": "raw answer",\n  "claimed_verdict": "pass",\n  "source_excerpt": "Concept Note / Lesson / Wiki excerpt"\n}}\n```\n'
                )
            else:
                detail_help = (
                    f"⛔ BLOCKED ({reject_code}) — {reject_detail}\n\n"
                    f"Dispatch a foreground GATE:review envelope via delegate_task on the exact content you wrote (generation-to-emission: write files first, review what was written, then report):\n"
                    f"```json\n"
                    f'{{\n  "gate": "review",\n  "concepts": ["Concept"],\n  "wiki_content": "exact written wiki text (must match the files on disk)",\n'
                    f'  "source_url": "https://...",\n  "lesson_ref": "Lessons/...md"\n}}\n```\n'
                    f"Grounding (source_url, source_file, or lesson_ref) is required, every concept must appear in wiki_content, "
                    f"and the written files must match the reviewed content. Applies to Clerk and Deputy alike."
                )

            assistant_msg["content"] = detail_help
            await self._bump_gate_state(chat_id, __user__, __request__, reject_code, parent_user_id)
            return body

        except Exception as e:
            # Fail open on unexpected gate internal error — don't block learner on bug
            try:
                import logging

                logging.getLogger(__name__).exception(f"gate_pipe outlet error: {e}")
            except Exception:
                pass
            return body

    # -----------------------------------------------------------------------
    # Gate state helpers (Chat.meta.gate_state) — per user turn
    # -----------------------------------------------------------------------

    async def _check_retry_cap(self, chat_id: str, user: dict | None, request, parent_user_msg_id: str | None):
        """Returns (should_retry: bool, cap_banner: str|None). Per-turn: different parent user msg resets."""
        try:
            if not chat_id or not user or request is None:
                return True, None
            from open_webui.models.chats import Chats

            chat = await Chats.get_chat_by_id_and_user_id(chat_id, user.get("id"))
            if not chat:
                return True, None
            state = (chat.meta or {}).get("gate_state") or {}
            # If turn changed, we wouldn't be here (reset happens at top), but handle stale state
            if parent_user_msg_id and state.get("last_user_msg_id") and state["last_user_msg_id"] != parent_user_msg_id:
                return True, None
            retries = int(state.get("retries", 0))
            max_retries = int(getattr(self.valves, "max_retries", 2))
            if retries >= max_retries:
                return False, getattr(self.valves, "blocked_banner", "⛔ Withheld: not independently verified — retry limit reached. Fix the GATE envelope and retry.")
            return True, None
        except Exception:
            return True, None

    async def _bump_gate_state(self, chat_id: str, user: dict | None, request, code: str, parent_user_msg_id: str | None):
        try:
            if not chat_id or not user or request is None:
                return
            from open_webui.internal.db import get_async_db
            from open_webui.models.chats import Chat
            from sqlalchemy import select

            async with get_async_db() as db:
                result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.get("id")))
                row = result.scalars().first()
                if not row:
                    return
                meta = dict(row.meta or {})
                state = dict(meta.get("gate_state") or {})
                # If turn changed since last bump, reset first
                if parent_user_msg_id and state.get("last_user_msg_id") and state["last_user_msg_id"] != parent_user_msg_id:
                    state = {}
                state["retries"] = int(state.get("retries", 0)) + 1
                state["last_code"] = code
                state["last_at"] = int(time.time())
                if parent_user_msg_id:
                    state["last_user_msg_id"] = parent_user_msg_id
                meta["gate_state"] = state
                row.meta = meta
                await db.commit()
        except Exception:
            pass

    async def _reset_gate_state(self, chat_id: str, user: dict | None, request):
        try:
            if not chat_id or not user or request is None:
                return
            from open_webui.internal.db import get_async_db
            from open_webui.models.chats import Chat
            from sqlalchemy import select

            async with get_async_db() as db:
                result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.get("id")))
                row = result.scalars().first()
                if not row or not (row.meta or {}).get("gate_state"):
                    return
                meta = dict(row.meta or {})
                meta.pop("gate_state", None)
                row.meta = meta
                await db.commit()
        except Exception:
            pass
