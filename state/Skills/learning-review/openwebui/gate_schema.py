"""
gate_schema — Pydantic schemas for deterministic delegation envelopes.

The Pipe (gate_pipe.py) validates envelopes against these schemas.
Subagent system prompt is keyed by GATE: type.

Envelope is native function-schema validated, not string sentinel.
"""

try:
    from pydantic import BaseModel, Field
except Exception as e:  # pragma: no cover
    raise ImportError("pydantic is required for gate_schema — install it or run inside Open WebUI") from e

import json
import re
from typing import List, Literal, Optional


# ---------------------------------------------------------------------------
# Fact-check envelope (Tutor → subagent)
# ---------------------------------------------------------------------------


class GateFactCheckClaim(BaseModel):  # type: ignore
    id: int = Field(description="Claim number, 1-indexed, contiguous")
    claim: str = Field(description="Single load-bearing claim text")


class GATEFactCheckEnvelope(BaseModel):  # type: ignore
    gate: Literal["fact_check"] = Field(default="fact_check")
    claims: List[GateFactCheckClaim] = Field(min_length=1)
    # Post-generation binding (2026-09): the actual draft step text being verified.
    # The verifier checks claims[] AS STATED in rendered_content, and the Pipe checks
    # rendered_content against the emitted message. Closes plan-vs-output drift.
    rendered_content: str = Field(
        min_length=1,
        description="Actual draft step text under verification (what will be rendered, pre-corrections)",
    )
    # At least one source must be set; multi-source (Rohit + external refs) preferred.
    # Singular fields are legacy; source_urls is the multi-source form.
    source_url: Optional[str] = Field(default=None, description="Stable URL to fetch")
    source_urls: Optional[List[str]] = Field(default=None, description="Multiple source URLs (Rohit + external refs) to verify against together")
    source_file: Optional[str] = Field(default=None, description="Repo-relative path")
    reference_excerpt: Optional[str] = Field(
        default=None, description="Optional excerpt — subagent validates against fetched source"
    )
    context: Optional[str] = Field(default=None, description="What is being taught and why")


class GATEFactCheckVerdictItem(BaseModel):  # type: ignore
    id: int
    verdict: Literal["PASS", "ISSUES", "UNVERIFIED"]
    explanation: str
    corrected_claim: Optional[str] = None


class GATEFactCheckVerdicts(BaseModel):  # type: ignore
    verdicts: List[GATEFactCheckVerdictItem]


# ---------------------------------------------------------------------------
# Review envelope (Clerk → subagent)
# ---------------------------------------------------------------------------


class GATEReviewEnvelope(BaseModel):  # type: ignore
    gate: Literal["review"] = Field(default="review")
    concepts: List[str] = Field(min_length=1)
    wiki_content: str = Field(min_length=1)
    source_url: Optional[str] = None
    source_file: Optional[str] = None
    lesson_ref: Optional[str] = Field(default=None, description="Lessons/Lesson — *.md path")
    pass_number: int = Field(default=1, ge=1, le=2)


class GATEReviewVerdict(BaseModel):  # type: ignore
    verdict: Literal["PASS", "ISSUES"]
    issues: List[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Review-session envelope (Clerk review flow → subagent)
# ---------------------------------------------------------------------------


class GATEReviewSessionFile(BaseModel):  # type: ignore
    path: str = Field(description="Repo-relative path of a review artifact written this session")
    content: str = Field(min_length=1, description="Exact written text of this artifact")


class GATEReviewSessionEnvelope(BaseModel):  # type: ignore
    gate: Literal["review_session"] = Field(default="review_session")
    concepts: List[str] = Field(min_length=1, description="Concepts reviewed this session")
    transcript: str = Field(
        min_length=1,
        description="Exact Q/A + learner answers + claimed verdicts for this session (generation-to-emission)",
    )
    grade_verdicts: List[dict] = Field(
        default_factory=list,
        description="One per concept: {concept, correct_verdict} from the grade-audit receipts",
    )
    written_files: List[GATEReviewSessionFile] = Field(
        min_length=1,
        description="Review notes / session note / touched state rows written this session (path + exact text)",
    )
    state_rows: Optional[str] = Field(
        default=None,
        description="Exact touched Active Concepts / Mistakes / Attempts text (optional)",
    )
    pass_number: int = Field(default=1, ge=1, le=2)


class GATEReviewSessionVerdict(BaseModel):  # type: ignore
    verdict: Literal["PASS", "PASS_WITH_FLAGS", "ISSUES"]
    issues: List[dict] = Field(default_factory=list)
    context_notes: List[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Quiz-audit envelope (Tutor → subagent, probe & end-of-lesson quiz)
# ---------------------------------------------------------------------------


class GateQuizQuestion(BaseModel):  # type: ignore
    id: str = Field(description="Question id, e.g. q1")
    type: Literal["mcq", "free_recall"] = Field(description="MCQ or free-recall item")
    question: str = Field(min_length=1)
    options: Optional[List[str]] = Field(default=None, description="4 options for MCQ")
    correct_index: Optional[int] = Field(default=None, description="0-indexed correct slot for MCQ")
    target_bloom: Optional[str] = Field(default=None)


class GATEQuizAuditEnvelope(BaseModel):  # type: ignore
    gate: Literal["quiz_audit"] = Field(default="quiz_audit")
    questions_json: List[GateQuizQuestion] = Field(min_length=1, description="Each: id, type mcq|free_recall, question, options+correct_index for MCQ, target_bloom")
    purpose: Literal["probe", "end-of-lesson quiz"] = Field(default="probe")
    concept: str = Field(description="Concept being probed")
    bloom_levels: List[str] = Field(default_factory=list)
    source_excerpt: str = Field(min_length=1)


class GATEQuizAuditVerdict(BaseModel):  # type: ignore
    verdict: Literal["PASS", "ISSUES"]
    issues: List[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Grade-audit envelope (Tutor review grading → subagent)
# ---------------------------------------------------------------------------


class GATEGradeAuditEnvelope(BaseModel):  # type: ignore
    gate: Literal["grade_audit"] = Field(default="grade_audit")
    concept: str = Field(description="Concept that was reviewed")
    question: str = Field(min_length=1, description="Question asked")
    learner_answer: str = Field(min_length=1, description="Learner's raw answer")
    claimed_verdict: Literal["pass", "fail"] = Field(description="Tutor's grade")
    source_excerpt: str = Field(min_length=1, description="Grounding excerpt (Concept Note / Lesson / Wiki)")
    feynman_transcript: Optional[str] = Field(default=None, description="Explain-back text for concept/design types")


class GATEGradeAuditVerdict(BaseModel):  # type: ignore
    verdict: Literal["PASS", "ISSUES"]
    agrees: bool = Field(description="True when claimed_verdict matches evidence")
    correct_verdict: Literal["pass", "fail"]
    issues: List[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Legacy helpers: validate sentinel text and JSON extraction (for migration)
# ---------------------------------------------------------------------------

_ENVELOPE_SENTINEL_RE = re.compile(r"^\s*GATE:(fact_check|review|review_session|quiz_audit|grade_audit)\b", re.MULTILINE)


def detect_gate_type(task_text: str) -> Optional[str]:
    m = _ENVELOPE_SENTINEL_RE.search(task_text or "")
    return m.group(1) if m else None


def extract_json_block(text: str) -> Optional[dict]:
    """Extract first JSON object from text, handling fences and fragments."""
    if not text:
        return None
    text = text.strip()
    # fence
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except Exception:
            pass
    # raw object
    if not text.startswith('"'):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                pass
    # bare fragment
    try:
        return json.loads(text)
    except Exception:
        pass
    # wrap fragment
    wrapped = "{" + text.strip()
    if not wrapped.rstrip().endswith("}"):
        wrapped = wrapped.rstrip().rstrip(",") + "}"
    try:
        return json.loads(wrapped)
    except Exception:
        return None
