#!/usr/bin/env python3
"""Batch file ops for the learning-system workspace (open-terminal sidecar).

Purpose: collapse many sequential read/write tool calls into ONE command so
agent sessions stay far below the model's cumulative context limit.

Usage:
  ops.py state TRACK              Standard session-start bundle for TRACK (aiefs|aie|swe).
                                  One call replaces: Learning Profile read, Active
                                  Concepts track slice, Attempts.json, Mistakes.md,
                                  log tail, index head.
  ops.py state TRACK --review     Compact review-session context: Learning Profile +
                                  the computed due queue (same as `queue`). Use this
                                  instead of the full `state` dump when starting a
                                  /review session.
  ops.py queue TRACK [--date YYYY-MM-DD] [--slots N] [--json] [--digest PATH]
                                  Compute the deterministic review queue: up to 2
                                  priority-1 due mistakes (oldest first) then due
                                  reviews from Attempts.json, shuffled with a
                                  same-Source adjacency guard and per-concept
                                  question-type alternation. Prints a human table
                                  (default), the queue JSON (--json), or writes the
                                  review digest skeleton to PATH (--digest).
  ops.py bundle SPEC [SPEC...]    Read many targets in one call. SPEC syntax:
                                    PATH            whole file
                                    PATH:N-M        lines N..M (1-based, inclusive)
                                    PATH:-N         last N lines
                                    PATH@REGEX      lines matching REGEX (ignore-case)
   ops.py apply < SPEC.json        Apply a batch of writes from JSON on stdin:
                                     {"writes":   [{"path": "...", "content": "..."}],
                                      "appends":  [{"path": "...", "content": "..."}],
                                      "replaces": [{"path": "...", "find": "...",
                                                    "replace_with": "..."}]}
                                   Prints a per-op summary. Use with a quoted heredoc.
  ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date YYYY-MM-DD] [--qtype TYPE] [--type memory|concept|procedure|design] [--confidence sure|hunch|no-idea] [--hints N] [--mode normal|solo] [--targets n_…,arg_…] [--prereq NAME ...]
                                   Record one answer in Attempts.json (interval_index
                                   +1 pass / +2 on 2 consecutive passes / -1 fail,
                                   next_review from type schedule). --qtype is
                                   validated against the enum (legacy aliases are
                                   normalized; unknown values are rejected). --targets
                                   records the knowledge-graph ids (n_… propositions /
                                   arg_… chains) the item retrieved; ids must be
                                   well-formed AND live in the graph ledger (a
                                   missing or retracted id is rejected). --prereq
                                   (repeatable) records the concept's direct prerequisite
                                   edges. Prints mastery + next_review for the skill to
                                   copy via apply.
  ops.py amend "Concept" --date OLD [--new-date NEW] [--field FIELD --value VALUE] --reason "..." [--occurrence N] [--json]
                                   Audited in-place correction of ONE recorded attempt:
                                   re-date it and/or fix a metadata field (date|q_type|
                                   confidence|hints|mode|targets), appending a `meta.amendments`
                                   record with the reason. Recomputes last_reviewed /
                                   next_review. This replaces the ad-hoc, gitignored
                                   `.tmp/gen_review_*.py` surgery scripts (RETIRED — do
                                   not rewrite Attempts.json outside ops.py). Correctness
                                   (result/is_correct) is not amendable; re-grade instead.
  ops.py grade-mcq --key A,B,C --answers A,C,C [--json]
                                   Deterministic MCQ grading: per-item pass/fail for a
                                   comma-separated answer key vs the learner's answers
                                   (empty/`-` = unanswered). No LLM in the mechanical
                                   path. Prints correct/total + per-item rows.
  ops.py prereqs "Concept" [--set NAME,...] [--json]
                                   Report the concept's direct prerequisites and their
                                   live state (solid|neutral|fuzzy|unknown). `blocks`
                                   is true when a direct prereq is fuzzy or has an open
                                   mistake, so a flow can refuse to advance. --set
                                   writes the prereq list; missing evidence is unknown
                                   (advisory, never blocks).
  ops.py calibration [TRACK] [--json]
                                   Confidence calibration: for attempts tagged with a
                                   confidence, % correct when `sure` vs `hunch` (and
                                   `no-idea`), with an over/under-confidence flag.
  ops.py mastery [TRACK] [--json]  Advisory mastery report: recency-weighted
                                   score plus per-dimension (recall, conceptual,
                                   procedural, transfer, independence, stability)
                                   from the attempt evidence. --json for machines
                                   (also carries per-concept calibration + transfer
                                   state). (0.00-1.00 + Feynman status, not blocking).

All paths resolve under the workspace root (/home/user/learning-system). Escapes are rejected.
"""

import hashlib
import json
import os
import random
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def _detect_root() -> Path:
    """Resolve the learning-system workspace root.

    The real checkout lives at /home/delinux/learning-system locally but at
    /home/user/learning-system inside the Open WebUI Open Terminal container, so
    hardcoding one path breaks the other. Auto-detect by looking for the
    distinctive 'Learning System/Core' substructure; honor an env override.
    """
    dynamic = []
    script_path = Path(__file__).resolve()
    dynamic.extend(str(p) for p in (script_path.parent, *script_path.parents))
    cwd = Path.cwd().resolve()
    dynamic.extend(str(p) for p in (cwd, *cwd.parents))

    candidates = [
        os.environ.get("LEARNING_SYSTEM_ROOT", ""),
        *dynamic,
        "/home/delinux/learning-system",
        "/home/user/learning-system",
        os.path.expanduser("~/learning-system"),
    ]
    for c in candidates:
        c = (c or "").strip()
        if c and os.path.isdir(os.path.join(c, "Learning System", "Core")):
            return Path(c).resolve()
    # Degenerate fallback: no checkout with the expected substructure was found
    # (e.g. a misconfigured environment). Best-effort the canonical container path
    # rather than crashing; callers will then see MISSING reads, not a stack trace.
    return Path("/home/user/learning-system").resolve()


ROOT = _detect_root()
MAX_LINE = 4000

DEFAULT_INTERVALS = {
    "memory": [0, 1, 3, 7, 14, 30, 60],
    "concept": [3, 7, 14, 30],
    "procedure": [3, 7, 14],
    "design": [14, 28],
}
ATTEMPTS_PATH = "Learning System/Core/Attempts.json"
MISTAKES_PATH = "Learning System/Core/🧯 Mistakes.md"
ACTIVE_PATH = "Learning System/Core/📚 Active Concepts.md"
WIKI_DIR = "Knowledge Wiki/wiki"
MASTERY_WEIGHTS = [0.4, 0.25, 0.15, 0.1, 0.1]
ERROR_TYPES = ("structural", "deviation", "application", "metacognitive")
# Attempt fields `ops.py amend` may correct in place. Correctness is deliberately
# NOT here: fixing a wrong pass/fail is a re-grade, not a typo fix — record a new
# attempt instead. Re-dating and metadata fixes are the audited amend path that
# replaces ad-hoc `.tmp/gen_review_*.py` state surgery.
AMENDABLE_ATTEMPT_FIELDS = ("date", "q_type", "confidence", "hints", "mode", "targets")
PREREQ_MARKER_RE = re.compile(r"^\s*\[prereq:\s*([^\]]+?)\s*\]\s*", re.I)

# Question types that evidence each mastery dimension (P0.4). Untagged or
# unknown q_types count toward recall only. Dimensions without any evidencing
# attempt report None ("unknown"), never a false zero.
#
# The canonical enum (P1.2) is enforced in `ops.py attempt`; legacy aliases
# (`free_recall`, `transfer`, `novel`, `error_detect`, `recall-mcq`, …) are
# normalized to canonical form. The dimension sets keep the legacy spellings too
# so already-stored attempts keep counting.
Q_TYPES = (
    "definitional",
    "discriminative",
    "computational",
    "free-recall",
    "transfer-near",
    "transfer-far",
    "explain-back",
    "error-detect",
    "micro-check",
    "applied",
    "procedure",
)
Q_TYPE_ALIASES = {
    "free_recall": "free-recall",
    "recall-mcq": "definitional",
    "recall_mcq": "definitional",
    "transfer": "transfer-near",
    "novel": "transfer-far",
    "error_detect": "error-detect",
    "explain_back": "explain-back",
}
RECALL_Q_TYPES = {"definitional", "free-recall", "free_recall", "recall-mcq", "recall_mcq", "micro-check"}
PROCEDURAL_Q_TYPES = {"computational", "applied", "procedure"}
TRANSFER_Q_TYPES = {"transfer", "transfer-near", "transfer-far", "novel", "error-detect", "error_detect"}
TRANSFER_FAR_Q_TYPES = {"transfer-far", "novel"}
EXPLAIN_BACK_Q_TYPES = {"explain-back", "explain_back"}
CONFIDENCE_LEVELS = ("sure", "hunch", "no-idea")


def normalize_qtype(qtype):
    """Canonical q_type, or None when unknown/empty.

    Legacy aliases map to canonical form; an unrecognized value returns None so
    the caller can reject it with a clear error."""
    if qtype is None:
        return None
    q = str(qtype).strip().lower()
    if not q:
        return None
    q = Q_TYPE_ALIASES.get(q, q)
    return q if q in Q_TYPES else None


def normalize_confidence(confidence):
    """Normalise `sure` / `hunch` / `no idea` (→ `no-idea`). Unknown values are
    returned lowercased, never rejected (back-compat)."""
    if confidence is None:
        return None
    c = str(confidence).strip().lower().replace(" ", "-")
    if not c:
        return None
    if c == "noidea":
        c = "no-idea"
    return c


# Knowledge-graph record ids: content-derived propositions (`n_…`) and reasoning
# chains (`arg_…`). Attempts may carry the ids an item retrieved; this is the
# bridge from practice items to per-node mastery. Malformed ids are rejected so a
# typo cannot silently create a phantom target, and ids are checked against the
# live ledger so a stale (missing or retracted) record cannot be recorded either.
GRAPH_TARGET_RE = re.compile(r"^(?:n|arg)_[a-z0-9]{6,}$")
GRAPH_DIR = Path("Knowledge Wiki") / "graph"
GRAPH_NODES_FILE = "nodes.jsonl"
GRAPH_CHAINS_FILE = "chains.jsonl"


def normalize_targets(targets):
    """Canonical graph-target id list, or None when empty.

    Accepts a list or a comma/space-separated string. Deduplicates and sorts.
    Raises ValueError naming the first malformed id (the caller rejects it)."""
    if targets is None:
        return None
    if isinstance(targets, str):
        targets = re.split(r"[,\s]+", targets)
    clean = []
    for target in targets:
        tid = str(target).strip()
        if not tid:
            continue
        if not GRAPH_TARGET_RE.match(tid):
            raise ValueError(tid)
        clean.append(tid)
    return sorted(set(clean)) or None


def _read_graph_jsonl(path):
    """Parsed JSON objects from a graph ledger; malformed lines are ignored.

    Liveness is a safety check, not the ledger's integrity audit (`graph.py
    status` owns that). A malformed line cannot make an id live."""
    records = []
    if not path.is_file():
        return records
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


# mirror: pinned by harness/graph_fold_test.py
def _chain_fingerprint(premises, conclusion):
    """Fingerprint `pi/graph.py` uses to decide re-assert vs new chain."""
    body = "\n".join(sorted(set(premises))) + "\n=>\n" + conclusion
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _chain_id(premises, conclusion):
    """Content-derived chain id, mirroring `pi/graph.py` (records without an id)."""
    return "arg_" + _chain_fingerprint(premises, conclusion)[:10]


def live_graph_ids(root=None):
    """Ids currently live in the knowledge-graph ledgers.

    Mirrors `pi/graph.py`'s append-only fold exactly: node `retract` tombstones
    and a later `define` revives, `link` never creates; a chain re-assert of the
    same premises/conclusion revives its existing id, while a *new* chain that
    happens to reuse a tombstoned id does not (graph.py does not pop the
    tombstone on the create path). Chains without a stored id are
    content-addressed the same way graph.py does it. Returns an empty set when
    the ledgers do not exist (no graph, no live ids).
    """
    base = Path(root) if root is not None else ROOT
    gdir = base / GRAPH_DIR

    live_nodes = set()
    retracted_nodes = set()
    for record in _read_graph_jsonl(gdir / GRAPH_NODES_FILE):
        ident = record.get("id")
        if not isinstance(ident, str) or not GRAPH_TARGET_RE.match(ident):
            continue
        op = record.get("op", "define")
        if op == "retract":
            retracted_nodes.add(ident)
        elif op == "define":
            retracted_nodes.discard(ident)
            live_nodes.add(ident)
        # `link` only annotates an existing proposition; it never creates one.

    live_chains = set()
    retracted_chains = set()
    chain_by_fingerprint = {}
    for record in _read_graph_jsonl(gdir / GRAPH_CHAINS_FILE):
        op = record.get("op", "assert")
        ident = record.get("id")
        if op == "retract":
            if isinstance(ident, str):
                retracted_chains.add(ident)
            continue
        if op != "assert":
            continue
        premises = record.get("premises")
        conclusion = record.get("conclusion")
        if (
            not isinstance(premises, list)
            or not premises
            or not all(isinstance(p, str) and p for p in premises)
            or not isinstance(conclusion, str)
            or not conclusion
        ):
            continue
        fingerprint = _chain_fingerprint(premises, conclusion)
        if fingerprint in chain_by_fingerprint:
            existing = chain_by_fingerprint[fingerprint]
            retracted_chains.discard(existing)
            live_chains.add(existing)
            continue
        resolved = ident if isinstance(ident, str) and GRAPH_TARGET_RE.match(ident) else _chain_id(
            premises, conclusion
        )
        live_chains.add(resolved)
        chain_by_fingerprint[fingerprint] = resolved

    return (live_nodes - retracted_nodes) | (live_chains - retracted_chains)


def check_targets_live(targets):
    """Raise ValueError naming every target id that is not live.

    This is the liveness half of target validation: a syntactically valid but
    stale id (missing from the ledger, or retracted) must never be recorded.
    Naming the whole stale set lets the caller drop them in one retry."""
    if not targets:
        return
    live = live_graph_ids()
    stale = [tid for tid in targets if tid not in live]
    if stale:
        raise ValueError(", ".join(stale))


def _resolve(p: str) -> Path:
    path = (ROOT / p).resolve() if not p.startswith("/") else Path(p).resolve()
    if ROOT not in path.parents and path != ROOT:
        raise ValueError(f"path escapes workspace: {p}")
    return path


def _read_lines(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.splitlines(), text


def _section_slice(lines, pattern):
    """Return the slice from a heading matching `pattern` up to the next heading
    of equal-or-higher level (so a track section captures its table body, not
    just the heading line). Returns (text, error)."""
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return None, f"BAD REGEX: {e}"
    headings = [i for i, l in enumerate(lines) if re.match(r"^#{1,6}\s", l)]
    start = None
    for i in headings:
        if rx.search(lines[i]):
            start = i
            break
    if start is None:
        return None, "(no matching section)"
    level = (len(lines[start]) - len(lines[start].lstrip("#"))) or 1
    end = len(lines)
    for j in headings:
        if j > start and (len(lines[j]) - len(lines[j].lstrip("#"))) <= level:
            end = j
            break
    return "\n".join(lines[start:end]), None


def do_state(track: str) -> None:
    track = track.lower().strip()
    if track == "aiefs":
        # Active AIEFS concepts live under per-lesson headings (Mission 0
        # Catch-Up, Phase 1 …), not a single `## aiefs` heading — pull the
        # live concept tables wholesale instead of one section.
        concept_spec = ("Learning System/Core/📚 Active Concepts.md@^\\| ", "")
    else:
        concept_spec = (f"Learning System/Core/📚 Active Concepts.md#^## {track}\\b", "")
    specs = [
        ("Learning System/Core/💡 Learning Profile.md", ""),
        # Section selector (#heading) pulls the whole track block (header + table
        # rows) — the old `^## {track}\b|^### ` grep matched only heading lines.
        concept_spec,
        (ATTEMPTS_PATH, ""),
        (MISTAKES_PATH, ""),
        ("Knowledge Wiki/log.md:-25", ""),
        ("Knowledge Wiki/index.md:1-40", ""),
    ]
    for spec, _ in specs:
        do_bundle(spec)


def do_bundle(*specs: str) -> None:
    for spec in specs:
        spec = spec.strip()
        path_part, note, selector = spec, "whole file", None

        if "#" in spec:
            path_part, pattern = spec.split("#", 1)
            note, selector = f"section /{pattern}/i", ("section", pattern)
        elif "@" in spec:
            path_part, pattern = spec.rsplit("@", 1)
            note, selector = f"grep /{pattern}/i", ("grep", pattern)
        else:
            m = re.search(r":(\d+)?-(\d+)?$", spec)
            if m:
                a, b = m.group(1), m.group(2)
                path_part = spec[: m.start()]
                if a is None:  # :-N -> last N lines
                    note, selector = f"last {b} lines", ("tail", int(b))
                else:  # :N-M or :N-
                    lo = int(a)
                    hi = int(b) if b else None
                    note = f"lines {lo}-{hi or 'end'}"
                    selector = ("range", lo, hi)

        path = _resolve(path_part)
        print(f"===== FILE: {path_part} [{note}] =====")
        if not path.is_file():
            print("MISSING")
            continue
        lines, text = _read_lines(path)
        total = len(lines)

        if selector is None:
            out = text
        elif selector[0] == "tail":
            out = "\n".join(lines[-selector[1]:])
        elif selector[0] == "range":
            lo, hi = selector[1], selector[2] or total
            lo = max(1, lo)
            out = "\n".join(lines[lo - 1: hi])
        elif selector[0] == "section":
            out, err = _section_slice(lines, selector[1])
            if err:
                print(err)
                continue
        else:  # grep
            try:
                rx = re.compile(selector[1], re.IGNORECASE)
            except re.error as e:
                print(f"BAD REGEX: {e}")
                continue
            hits = [(i + 1, ln) for i, ln in enumerate(lines) if rx.search(ln)]
            out = "\n".join(f"{i}: {ln[:MAX_LINE]}" for i, ln in hits) if hits else "(no matches)"
            print(f"({len(hits)} matching lines)")
            print(out)
            continue

        print(out if out else "(empty)")


def _load_attempts() -> tuple:
    p = _resolve(ATTEMPTS_PATH)
    if not p.is_file():
        return {"concepts": {}, "meta": {"version": 1, "intervals": DEFAULT_INTERVALS}}, p
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("concepts", {})
    meta = data.setdefault("meta", {})
    meta.setdefault("intervals", DEFAULT_INTERVALS)
    return data, p


def _intervals_for(data: dict, ctype: str):
    sched = (data.get("meta") or {}).get("intervals") or DEFAULT_INTERVALS
    return sched.get(ctype, sched.get("concept", [3, 7, 14, 30]))


def _recent_correctness(attempts: list) -> float:
    """Recency-weighted correctness 0-1 over the last (up to 5) attempts."""
    if not attempts:
        return 0.0
    recent = attempts[-5:][::-1]  # most recent first
    weights = MASTERY_WEIGHTS[: len(recent)]
    total = sum(weights)
    return sum(w * (1.0 if a.get("is_correct") else 0.0) for w, a in zip(weights, recent)) / total


def compute_mastery(attempts: list) -> float:
    """Recency-weighted mastery 0-1 with confidence caps ({1:0.5, 2:0.8})."""
    if not attempts:
        return 0.0
    score = _recent_correctness(attempts)
    n = len(attempts)
    if n == 1:
        score = min(score, 0.5)
    elif n == 2:
        score = min(score, 0.8)
    return round(score, 2)


def _feynman_state(entry: dict):
    """Normalise the feynman field to True/False/None."""
    f = entry.get("feynman")
    if isinstance(f, dict):
        f = f.get("pass")
    if f in (True, "pass"):
        return True
    if f in (False, "fail"):
        return False
    return None


def compute_dimensions(entry: dict) -> dict:
    """Per-dimension mastery (0-3, or None when no evidence exists).

    Advisory, heuristic, and deliberately explicit about its inputs (P0.4):
      recall        recency-weighted correctness of recall-type attempts
      conceptual    driven by the Feynman explain-back flag (or explain-back items)
      procedural    correctness of computational/applied/procedure attempts
      transfer      correctness of transfer-near/far + error-detect attempts
      independence  the last AI-free (mode="solo") attempt; None if never tested
      stability     interval_index (how long a gap the concept has survived)
    A dimension with no evidencing attempt is None (unknown), never 0, so an
    untested dimension cannot masquerade as a failed one."""
    attempts = entry.get("attempts", []) or []

    def dim(sel):
        if not sel:
            return None
        return int(round(3 * _recent_correctness(sel)))

    recall_sel = [a for a in attempts if (a.get("q_type") in RECALL_Q_TYPES) or not a.get("q_type")]
    solo = [a for a in attempts if a.get("mode") == "solo"]
    conceptual = None
    feyn = _feynman_state(entry)
    if feyn is not None:
        conceptual = 3 if feyn else 0
    else:
        explain = [a for a in attempts if a.get("q_type") in EXPLAIN_BACK_Q_TYPES]
        if explain:
            conceptual = dim(explain)
    return {
        "recall": dim(recall_sel),
        "conceptual": conceptual,
        "procedural": dim([a for a in attempts if a.get("q_type") in PROCEDURAL_Q_TYPES]),
        "transfer": dim([a for a in attempts if a.get("q_type") in TRANSFER_Q_TYPES]),
        "independence": (3 if solo[-1].get("is_correct") else 0) if solo else None,
        # Stability has no evidencing attempt for a concept with no history, so it
        # is None (unknown), never a false 0 — matching the docstring and the
        # other dimensions.
        "stability": min(3, int(entry.get("interval_index", 0) or 0)) if attempts else None,
    }


def transfer_ok(entry: dict) -> bool:
    """True when at least one passed far-transfer attempt is on record (P1.5).

    `consolidated` graduation (when it exists) requires a delayed far-transfer
    pass, so near-isomorphic-only evidence cannot consolidate a concept. Absence
    of far-transfer evidence is *unknown*, not failure, and does not block."""
    return any(
        a.get("is_correct") and a.get("q_type") in TRANSFER_FAR_Q_TYPES
        for a in (entry.get("attempts", []) or [])
    )


def independence_ok(entry: dict) -> bool:
    """False only when a failed AI-free (solo) attempt is on record.

    Absence of solo evidence is *unknown*, not failure, so existing concepts
    are grandfathered until `/solo` produces a real test (P0.4/P0.5)."""
    return compute_dimensions(entry).get("independence") != 0


def _parse_date(s: str):
    s = (s or "").strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_table_rows(path: Path, min_cols: int):
    """Parse markdown table rows into cell lists, skipping the header and the
    separator row. Cells are split on '|'; ragged rows shorter than min_cols are
    dropped. The caller is responsible for joining any over-flowing trailing
    cells (e.g. free-text notes that contain a literal '|')."""
    if not path.is_file():
        return []
    rows = []
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < min_cols:
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c != ""):
            continue
        rows.append(cells)
    return rows


def _track_matches(row_track: str, track: str) -> bool:
    rt = (row_track or "").lower().strip()
    t = track.lower().strip()
    if t in ("aiefs", "aie"):
        return rt in ("aiefs", "aie")
    return rt == t


def _active_rows(track: str):
    """Return (track_rows map, all_rows list) parsed from Active Concepts.md."""
    rows = _parse_table_rows(_resolve(ACTIVE_PATH), 8)
    all_rows, track_rows = [], {}
    for c in rows:
        if c[0].lower() == "concept":
            continue
        rec = {
            "concept": c[0], "track": c[1], "type": c[2], "status": c[3],
            "source": c[4], "last_reviewed": c[5], "next_review": c[6],
            "last_q_type": c[7], "notes": " | ".join(c[8:]).strip(),
        }
        all_rows.append(rec)
        track_rows[rec["concept"]] = rec
    if track:
        track_rows = {k: v for k, v in track_rows.items() if _track_matches(v["track"], track)}
    return track_rows, all_rows


def _extract_prereq(text: str):
    """Split a `[prereq: NAME]` marker off the front of a self-attribution cell.

    The Clerk may prefix a Mistakes row's Self-Attribution with
    `[prereq: <name>]` to link the mistake to the prerequisite it exposes (P2.8).
    Returns (prereq, rest); prereq is "" when the marker is absent. Kept as a
    cell prefix (not a new column) so existing rows need no schema migration."""
    m = PREREQ_MARKER_RE.match(text or "")
    if not m:
        return "", text or ""
    return m.group(1).strip(), (text or "")[m.end():].lstrip()


def _mistakes_rows_from(path: Path):
    """Parse one mistakes ledger file. error_type is located by matching the
    enum (robust to literal '|' in the question/expected/self-attribution
    cells); status/retries/next_retry are always the last three cells. An
    optional `[prereq: NAME]` prefix on Self-Attribution links the mistake to
    the prerequisite it exposes (P2.8); `prereq` is "" when absent.

    Shared with learner_history.py so the live and archived ledgers are read
    by one rule instead of by a fixed column index."""
    rows = _parse_table_rows(path, 9)
    out = []
    for c in rows:
        if c[0].lower() == "date":
            continue
        idx = next((i for i in range(4, len(c)) if c[i].lower() in ERROR_TYPES), None)
        if idx is None or len(c) < 9:
            continue
        prereq, attribution = _extract_prereq(" | ".join(c[idx + 1:len(c) - 3]))
        out.append({
            "date": c[0], "concept": c[1], "question": c[2],
            "expected": " | ".join(c[3:idx]),
            "error_type": c[idx].lower(),
            "self_attribution": attribution,
            "prereq": prereq,
            "status": c[-3].lower(), "retries": c[-2], "next_retry": c[-1],
        })
    return out


def _mistakes_rows():
    """Parse the live mistakes ledger (see `_mistakes_rows_from`)."""
    return _mistakes_rows_from(_resolve(MISTAKES_PATH))


def _source_key(entry: dict) -> str:
    """Normalize the Source column so the adjacency guard compares the same
    lesson/mission origin: drop the language parenthetical, prefer a
    'rohit pn lnn' token, else the lowercased text."""
    src = (entry.get("source") or "").lower()
    src = re.sub(r"\([^)]*\)", "", src)
    m = re.search(r"rohit\s+p\d+\s+l\d+", src)
    return (m.group(0) if m else src).strip()


def _concept_excerpt(name: str, notes: str) -> str:
    """Best-effort grounding excerpt for a queue entry: the wiki page's Insight
    line + first body paragraph, else the Active Concepts notes cell."""
    try:
        wiki = _resolve(WIKI_DIR)
        target = None
        direct = _resolve(f"{WIKI_DIR}/{name}.md")
        if direct.is_file():
            target = direct
        elif wiki.is_dir():
            files = os.listdir(wiki)
            low = name.lower()
            exact = [f for f in files if f.lower() == f"{low}.md"]
            fuzzy = [f for f in files if low in f.lower() or f[:-3].lower() in low]
            pick = (exact or fuzzy or [None])[0]
            if pick:
                target = _resolve(f"{WIKI_DIR}/{pick}")
        if target is not None and target.is_file():
            lines = [l.strip() for l in target.read_text(encoding="utf-8", errors="replace").splitlines()]
            insight = next((l for l in lines if "**Insight:**" in l), "")
            insight = re.sub(r"^>\s*", "", insight)
            body = [l for l in lines if l and not l.startswith(("#", ">", "|"))]
            parts = [insight] if insight else []
            if body:
                parts.append(" ".join(body[:3]))
            ex = " ".join(parts).strip()
            if ex:
                return ex[:500]
    except Exception:
        pass
    return (notes or "").strip()[:500]


def _question_type(last_q: str) -> str:
    """Alternate by Last Q Type: definitional -> discriminative; everything else
    (discriminative, computational, memory, blank) -> definitional."""
    return "definitional" if (last_q or "").strip().lower() == "discriminative" else "discriminative"


def _order_adjacency(entries, keyfn, initial_key=None):
    """Reorder so no two consecutive entries share a Source key whenever a valid
    arrangement exists (most-frequent-remaining-key first, never the previous
    key). Falls back to the remaining order when the constraint is impossible."""
    groups = {}
    for e in entries:
        groups.setdefault(keyfn(e), []).append(e)
    result = []
    last = initial_key
    while len(result) < len(entries):
        keys = [k for k, v in groups.items() if v]
        if not keys:
            break
        pickable = [k for k in keys if k != last] or keys
        best = max(pickable, key=lambda k: len(groups[k]))
        result.append(groups[best].pop(0))
        last = best
    return result


def _queue_entry(row: dict, attempts: dict, due_kind: str, mistake=None) -> dict:
    name = row["concept"]
    e = attempts.get(name, {}) or {}
    last_q = row.get("last_q_type") or ""
    ctype = row.get("type", "concept")
    qtype = _question_type(last_q)
    # P1.5: deterministic far-transfer cadence. For a concept/design concept
    # with no transfer attempt on record, every third review asks a
    # `transfer-far` item. The "use the queue verbatim" rule then has the
    # transfer item inside the queue instead of requiring the Tutor to improvise
    # against it.
    if due_kind == "review" and ctype in ("concept", "design"):
        hist = e.get("attempts", []) or []
        has_transfer = any(a.get("q_type") in TRANSFER_Q_TYPES for a in hist)
        if not has_transfer and len(hist) >= 3 and len(hist) % 3 == 0:
            qtype = "transfer-far"
    return {
        "concept": name,
        "type": ctype,
        "source": row.get("source", ""),
        "last_q_type": last_q,
        "question_type": qtype,
        "due_kind": due_kind,
        "last_reviewed": row.get("last_reviewed", ""),
        "next_review": e.get("next_review") or row.get("next_review", ""),
        "mastery": compute_mastery(e.get("attempts", [])),
        "feynman": e.get("feynman") or None,
        "error_type": (mistake or {}).get("error_type"),
        "self_attribution": (mistake or {}).get("self_attribution"),
        "prereq": (mistake or {}).get("prereq") or "",
        "source_excerpt": _concept_excerpt(name, row.get("notes", "")),
    }


def _build_queue(track: str, day: date, slots: int = 5) -> dict:
    """Compute the deterministic review queue and return the payload dict."""
    data, _ = _load_attempts()
    attempts = data.get("concepts", {})
    track = (track or "aiefs").lower().strip()
    track_rows, all_rows = _active_rows(track)
    notes = []

    # Slots 1-2: due mistakes (active/review, next retry <= day), oldest first,
    # one per concept.
    due_mistakes, seen = [], set()
    for m in sorted(_mistakes_rows(), key=lambda r: r["date"]):
        if m["status"] not in ("active", "review"):
            continue
        nr = _parse_date(m["next_retry"])
        if not nr or nr > day:
            continue
        if m["concept"] in seen:
            continue
        row = track_rows.get(m["concept"])
        if row is None:
            other = next((r for r in all_rows if r["concept"] == m["concept"]), None)
            if other is not None:
                notes.append(f"due mistake '{m['concept']}' is in track '{other['track']}', not '{track}'")
            else:
                notes.append(f"due mistake '{m['concept']}' has no Active Concepts row")
            continue
        seen.add(m["concept"])
        due_mistakes.append((m, row))
        if len(due_mistakes) >= 2:
            break

    # Remaining slots: due reviews from Attempts.json (scheduler truth).
    candidates = []
    for name, row in track_rows.items():
        if name in seen:
            continue
        e = attempts.get(name)
        if not e:
            if (_parse_date(row.get("next_review")) or date.max) <= day:
                notes.append(f"'{name}' due in Active Concepts ({row['next_review']}) but missing from Attempts.json")
            continue
        nr = _parse_date(e.get("next_review"))
        if nr and nr <= day:
            candidates.append((name, row, e))

    rng = random.Random(f"{track}:{day.isoformat()}")
    rng.shuffle(candidates)
    ordered = _order_adjacency(
        candidates, keyfn=lambda t: _source_key(t[1]),
        initial_key=_source_key(due_mistakes[-1][1]) if due_mistakes else None)

    queue = [_queue_entry(row, attempts, "mistake", m) for m, row in due_mistakes]
    for name, row, _e in ordered[:max(0, slots - len(queue))]:
        queue.append(_queue_entry(row, attempts, "review"))

    # Drift: Active Concepts next_review vs Attempts.json (scheduler truth).
    for name, row in track_rows.items():
        e = attempts.get(name)
        if e and row.get("next_review") and e.get("next_review") and row["next_review"] != e["next_review"]:
            notes.append(f"'{name}' Next Review {row['next_review']} (AC) != {e['next_review']} (Attempts)")

    # Dedupe + cap the drift notes (report, never fix).
    notes = list(dict.fromkeys(notes))[:12]

    return {
        "track": track, "date": day.isoformat(),
        "due_mistakes": len(due_mistakes), "due_reviews": len(queue) - len(due_mistakes),
        "slots": slots, "queue": queue, "warnings": notes,
    }


def do_queue(track: str, day: date, slots: int = 5, as_json: bool = False,
             digest_path: str = None) -> None:
    payload = _build_queue(track, day, slots)

    if digest_path:
        p = _resolve(digest_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        digest = {
            "track": payload["track"], "digest": digest_path,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "position": None, "queue": payload["queue"],
            "due_mistakes": payload["due_mistakes"], "due_reviews": payload["due_reviews"],
            "warnings": payload["warnings"],
        }
        p.write_text(json.dumps(digest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"WROTE {digest_path} ({len(payload['queue'])} queue entr"
              f"{'y' if len(payload['queue']) == 1 else 'ies'})")
        if not as_json:
            _print_queue_table(payload)
        return

    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    _print_queue_table(payload)


def _print_queue_table(payload: dict) -> None:
    q = payload["queue"]
    print(f"REVIEW QUEUE — track {payload['track']} — {payload['date']}    "
          f"({len(q)} slot(s): {payload['due_mistakes']} due mistake(s), {payload['due_reviews']} due review(s))")
    if not q:
        print("(nothing due — no mistakes or reviews on or before today)")
    for i, e in enumerate(q, 1):
        tail = f"mastery {e['mastery']:.2f}"
        if e["due_kind"] == "mistake":
            tail += f" · error_type {e['error_type']}"
        print(f"{i}. [{e['due_kind']}] {e['concept']} — {e['type']} · {e['source']} · "
              f"last Q {e['last_q_type'] or '—'} → ask {e['question_type']} · {tail}")
        if e.get("prereq"):
            print(f"     repair prereq: {e['prereq']} (re-derive it before the concept)")
        if e.get("self_attribution"):
            print(f"     self-attribution: {e['self_attribution'][:160]}")
    if payload["warnings"]:
        print("NOTES:")
        for n in payload["warnings"]:
            print(f" - {n}")


def do_attempt(concept: str, result: str, feynman: str = None, date: str = None,
               qtype: str = None, ctype: str = None, confidence: str = None,
               hints: int = None, mode: str = None, prereqs: list = None,
               targets: list = None) -> None:
    result = (result or "").lower().strip()
    if result not in ("pass", "fail"):
        print(f"ATTEMPT FAILED: result must be pass|fail, got {result!r}")
        sys.exit(2)
    if qtype is not None:
        normalized = normalize_qtype(qtype)
        if normalized is None:
            print(f"ATTEMPT FAILED: unknown --qtype {qtype!r}; expected one of: {', '.join(Q_TYPES)}")
            sys.exit(2)
        qtype = normalized
    confidence = normalize_confidence(confidence)
    if confidence is not None and confidence not in CONFIDENCE_LEVELS:
        print(f"ATTEMPT FAILED: unknown --confidence {confidence!r}; expected one of: {', '.join(CONFIDENCE_LEVELS)}")
        sys.exit(2)
    if mode is not None:
        mode = str(mode).strip().lower()
        if mode not in ("normal", "solo"):
            print(f"ATTEMPT FAILED: --mode must be normal|solo, got {mode!r}")
            sys.exit(2)
    try:
        targets = normalize_targets(targets)
    except ValueError as exc:
        print(f"ATTEMPT FAILED: bad --targets id {exc.args[0]!r}; "
              "expected graph ids like n_ab12cd34ef or arg_ab12cd34ef")
        sys.exit(2)
    try:
        check_targets_live(targets)
    except ValueError as exc:
        print(f"ATTEMPT FAILED: --targets id(s) {exc.args[0]!r} are not live in the knowledge graph "
              "(missing or retracted); use ids from `graph.py list`")
        sys.exit(2)
    is_correct = result == "pass"
    day = date or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        print(f"ATTEMPT FAILED: bad --date {day!r}, want YYYY-MM-DD")
        sys.exit(2)
    data, path = _load_attempts()
    entry = data["concepts"].get(concept)
    if entry is None:
        entry = {
            "type": (ctype or "concept").lower().strip(),
            "attempts": [],
            "interval_index": 0,
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "last_reviewed": day,
            "next_review": day,
            "feynman": None,
        }
        data["concepts"][concept] = entry
    if prereqs is not None:
        # Merge with existing edges: recording one prereq per attempt must not
        # silently drop the others (the graph would lose blocking edges).
        # `prereqs --set` keeps replace semantics.
        existing = entry.get("prereqs", []) or []
        entry["prereqs"] = sorted(set(existing) | {p for p in prereqs if p})
    if is_correct:
        entry["consecutive_correct"] = int(entry.get("consecutive_correct", 0)) + 1
        entry["consecutive_wrong"] = 0
        step = 2 if entry["consecutive_correct"] >= 2 else 1
        entry["interval_index"] = int(entry.get("interval_index", 0)) + step
    else:
        entry["consecutive_wrong"] = int(entry.get("consecutive_wrong", 0)) + 1
        entry["consecutive_correct"] = 0
        entry["interval_index"] = int(entry.get("interval_index", 0)) - 1
    sched = _intervals_for(data, entry.get("type", "concept"))
    entry["interval_index"] = max(0, min(int(entry["interval_index"]), len(sched) - 1))
    rec = {"date": day, "is_correct": is_correct, "result": result, "q_type": qtype}
    # Optional per-attempt evidence (P0.4): confidence tag, hints used, and
    # whether the attempt was AI-free ("solo"). Recorded only when supplied so
    # existing callers and stored attempts are unaffected.
    if confidence:
        rec["confidence"] = confidence
    if hints is not None:
        rec["hints"] = int(hints)
    if mode:
        rec["mode"] = mode
    if targets:
        rec["targets"] = targets
    entry["attempts"].append(rec)
    entry["last_reviewed"] = day
    entry["next_review"] = (datetime.strptime(day, "%Y-%m-%d").date()
                            + timedelta(days=sched[entry["interval_index"]])).isoformat()
    if feynman in ("feynman_pass", "feynman_fail"):
        entry["feynman"] = "pass" if feynman == "feynman_pass" else "fail"
    elif feynman is not None:
        print(f"ATTEMPT FAILED: feynman must be feynman_pass|feynman_fail, got {feynman!r}")
        sys.exit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mastery = compute_mastery(entry["attempts"])
    feyn = entry.get("feynman") or "—"
    print(f"ATTEMPT OK: {concept} {result} mastery {mastery:.2f} — Feynman: {feyn}")
    print(f"next_review {entry['next_review']} (interval_index {entry['interval_index']})")


def do_amend(concept: str, date: str, new_date: str = None, field: str = None,
             value: str = None, reason: str = None, occurrence: int = 1,
             as_json: bool = False) -> None:
    """Audited in-place correction of one recorded attempt (P2.5).

    Re-dates an attempt and/or fixes a metadata field (`date`, `q_type`,
    `confidence`, `hints`, `mode`), records who/why in `meta.amendments`, and
    recomputes `last_reviewed`/`next_review` from the attempt history. This is
    the first-class replacement for the ad-hoc `.tmp/gen_review_*.py` surgery
    scripts: every correction is logged and passes through ops.py rather than
    rewriting state outside any gate. Correctness (`result`/`is_correct`) is not
    amendable — that is a re-grade, recorded with `ops.py attempt`."""
    if not reason or not reason.strip():
        print("AMEND FAILED: --reason is required (the audit trail must say why)")
        sys.exit(2)
    old_date = _parse_date(date)
    if old_date is None:
        print(f"AMEND FAILED: bad --date {date!r}, want YYYY-MM-DD")
        sys.exit(2)
    if new_date is None and field is None:
        print("AMEND FAILED: give --new-date and/or --field FIELD --value VALUE")
        sys.exit(2)
    if field is not None:
        field = field.strip().lower()
        if field not in AMENDABLE_ATTEMPT_FIELDS:
            print(f"AMEND FAILED: --field must be one of: {', '.join(AMENDABLE_ATTEMPT_FIELDS)}")
            sys.exit(2)
        if value is None or value.strip() == "":
            print("AMEND FAILED: --field requires a non-empty --value")
            sys.exit(2)
    if new_date is not None:
        nd = _parse_date(new_date)
        if nd is None:
            print(f"AMEND FAILED: bad --new-date {new_date!r}, want YYYY-MM-DD")
            sys.exit(2)
        # A far-future re-date would silently hide the concept from SRS; allow a
        # one-day skew for timezone/session boundaries only.
        if nd > datetime.now().date() + timedelta(days=1):
            print(f"AMEND FAILED: --new-date {new_date!r} is in the future")
            sys.exit(2)

    data, path = _load_attempts()
    entry = data.get("concepts", {}).get(concept)
    if entry is None:
        print(f"AMEND FAILED: no Attempts.json entry for {concept!r}")
        sys.exit(2)
    matches = [a for a in entry.get("attempts", []) or [] if a.get("date") == date]
    if not matches:
        print(f"AMEND FAILED: {concept!r} has no attempt dated {date}")
        sys.exit(2)
    if occurrence < 1 or occurrence > len(matches):
        print(f"AMEND FAILED: --occurrence {occurrence} out of range (1..{len(matches)} on {date})")
        sys.exit(2)
    attempt = matches[occurrence - 1]

    changes = {}

    def set_field(name: str, new_value) -> None:
        if attempt.get(name) != new_value:
            changes[name] = [attempt.get(name), new_value]
            attempt[name] = new_value

    if field is not None:
        if field == "q_type":
            normalized = normalize_qtype(value)
            if normalized is None:
                print(f"AMEND FAILED: unknown --qtype {value!r}; expected one of: {', '.join(Q_TYPES)}")
                sys.exit(2)
            set_field("q_type", normalized)
        elif field == "confidence":
            normalized = normalize_confidence(value)
            if normalized not in CONFIDENCE_LEVELS:
                print(f"AMEND FAILED: --confidence must be one of: {', '.join(CONFIDENCE_LEVELS)}")
                sys.exit(2)
            set_field("confidence", normalized)
        elif field == "hints":
            try:
                hints_value = int(value)
            except ValueError:
                print(f"AMEND FAILED: --hints value must be an integer, got {value!r}")
                sys.exit(2)
            if hints_value < 0:
                print(f"AMEND FAILED: --hints must be non-negative, got {hints_value}")
                sys.exit(2)
            set_field("hints", hints_value)
        elif field == "mode":
            if value not in ("normal", "solo"):
                print(f"AMEND FAILED: --mode must be normal|solo, got {value!r}")
                sys.exit(2)
            set_field("mode", value)
        elif field == "targets":
            try:
                normalized_targets = normalize_targets(value)
            except ValueError as exc:
                print(f"AMEND FAILED: bad --targets id {exc.args[0]!r}; "
                      "expected graph ids like n_ab12cd34ef or arg_ab12cd34ef")
                sys.exit(2)
            try:
                check_targets_live(normalized_targets)
            except ValueError as exc:
                print(f"AMEND FAILED: --targets id(s) {exc.args[0]!r} are not live in the knowledge graph "
                      "(missing or retracted); use ids from `graph.py list`")
                sys.exit(2)
            set_field("targets", normalized_targets)
        elif field == "date":
            set_field("date", new_date or value)
    if new_date is not None:
        set_field("date", new_date)

    if not changes:
        print(f"AMEND NO-OP: {concept} attempt {date} already has the requested values")
        return

    # Recompute the schedule from the (possibly re-dated) attempt history so a
    # date fix cannot leave last_reviewed/next_review stale.
    dates = [a.get("date") for a in entry.get("attempts", []) or [] if _parse_date(a.get("date"))]
    if dates:
        last = max(dates)
        entry["last_reviewed"] = last
        sched = _intervals_for(data, entry.get("type", "concept"))
        idx = max(0, min(int(entry.get("interval_index", 0) or 0), len(sched) - 1))
        entry["next_review"] = (datetime.strptime(last, "%Y-%m-%d").date()
                                + timedelta(days=sched[idx])).isoformat()

    record = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "concept": concept,
        "attempt_date": date,
        "occurrence": occurrence,
        "changes": {k: {"from": v[0], "to": v[1]} for k, v in changes.items()},
        "reason": reason.strip(),
    }
    data.setdefault("meta", {}).setdefault("amendments", []).append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if as_json:
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return
    changed = ", ".join(f"{k}: {v[0]!r} → {v[1]!r}" for k, v in changes.items())
    print(f"AMEND OK: {concept} attempt {date} — {changed}")
    print(f"reason: {reason.strip()}")
    print(f"next_review {entry.get('next_review')} (last_reviewed {entry.get('last_reviewed')})")


def _track_concept_names(concepts: dict, track: str):
    """Concept names, filtered to a track's Active Concepts section when the
    track is given and the section resolves."""
    names = sorted(concepts)
    if not track:
        return names
    try:
        apath = _resolve("Learning System/Core/📚 Active Concepts.md")
        if apath.is_file():
            lines = apath.read_text(encoding="utf-8", errors="replace").splitlines()
            section, err = _section_slice(lines, rf"^## {re.escape(track)}\b")
            if not err and section:
                in_section = {n for n in names if n in section}
                if in_section:
                    names = sorted(in_section)
    except Exception:
        pass
    return names


def compute_calibration(attempts: list) -> dict:
    """Confidence calibration over attempts that carry a `confidence` tag (P1.4).

    Reports per-level counts/accuracy and flags `overconfident` when `sure` is
    wrong too often, or `underconfident` when `hunch` is right too often. Only
    tagged attempts count; untagged history is ignored (no false signal)."""
    buckets = {}
    untagged = 0
    for a in attempts or []:
        c = normalize_confidence(a.get("confidence"))
        if not c:
            untagged += 1
            continue
        b = buckets.setdefault(c, {"n": 0, "correct": 0})
        b["n"] += 1
        if a.get("is_correct"):
            b["correct"] += 1
    for b in buckets.values():
        b["accuracy"] = round(b["correct"] / b["n"], 2) if b["n"] else None
    flags = []
    sure = buckets.get("sure")
    if sure and sure["n"] >= 3 and (sure["n"] - sure["correct"]) / sure["n"] > 0.3:
        flags.append("overconfident")
    hunch = buckets.get("hunch")
    if hunch and hunch["n"] >= 3 and hunch["correct"] / hunch["n"] >= 0.75:
        flags.append("underconfident")
    # Untagged attempts are surfaced so a flow that silently drops the
    # confidence tag is visible, not just "no data".
    return {"buckets": buckets, "flags": flags, "untagged": untagged}


def _open_mistake_concepts() -> set:
    """Concept names with an active/review mistake row (the live queue)."""
    return {m["concept"] for m in _mistakes_rows() if m["status"] in ("active", "review")}


def _prereq_state(name: str, concepts: dict, open_mistakes: set) -> str:
    """Live state of a prerequisite concept: solid|neutral|fuzzy|unknown.

    Mirrors `learner_history.tag`'s strictness closely enough for the gate: an
    open mistake, a wrong streak, or a failed last attempt is `fuzzy`; two-plus
    consecutive correct at interval >= 2 (with Feynman for concept/design) is
    `solid`; no evidence at all is `unknown` (advisory — never blocks)."""
    entry = concepts.get(name)
    if entry is None:
        return "unknown"
    if name in open_mistakes:
        return "fuzzy"
    if int(entry.get("consecutive_wrong", 0) or 0) > 0:
        return "fuzzy"
    attempts = entry.get("attempts", []) or []
    if attempts and not attempts[-1].get("is_correct"):
        return "fuzzy"
    if (
        int(entry.get("consecutive_correct", 0) or 0) >= 2
        and int(entry.get("interval_index", 0) or 0) >= 2
        and (entry.get("type") in ("memory", "procedure") or _feynman_state(entry))
    ):
        return "solid"
    return "neutral"


def do_prereqs(concept: str, set_list=None, as_json: bool = False) -> None:
    """Report (or set) a concept's direct prerequisite edges and their state.

    `blocks` is true when a direct prereq is `fuzzy` (or has an open mistake): the
    teach/review flow must refuse to advance and re-derive the prereq first. A
    prereq with no evidence is `unknown` and never blocks (advisory)."""
    data, path = _load_attempts()
    concepts = data.get("concepts", {})
    entry = concepts.get(concept)
    if set_list is not None:
        if entry is None:
            entry = {
                "type": "concept",
                "attempts": [],
                "interval_index": 0,
                "consecutive_correct": 0,
                "consecutive_wrong": 0,
                "last_reviewed": "",
                "next_review": "",
                "feynman": None,
            }
            concepts[concept] = entry
        entry["prereqs"] = [p for p in set_list if p]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    prereqs = (entry or {}).get("prereqs", []) or []
    open_m = _open_mistake_concepts()
    states = [{"concept": p, "state": _prereq_state(p, concepts, open_m)} for p in prereqs]
    blocks = any(s["state"] == "fuzzy" for s in states)
    payload = {"concept": concept, "prereqs": states, "blocks": blocks}
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    if not prereqs:
        print(f"PREREQS {concept}: (none recorded)")
        return
    print(f"PREREQS {concept}: " + ("BLOCKS — re-derive a fuzzy prereq first" if blocks else "ok"))
    for s in states:
        print(f"  - {s['concept']}: {s['state']}")


def do_calibration(track: str = "", as_json: bool = False) -> None:
    """Aggregate confidence calibration for a track (or all concepts)."""
    data, _ = _load_attempts()
    concepts = data.get("concepts", {})
    names = _track_concept_names(concepts, track)
    attempts = []
    for n in names:
        attempts.extend(concepts[n].get("attempts", []) or [])
    cal = compute_calibration(attempts)
    payload = {"track": track or "all", "concepts": len(names), **cal}
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    print(f"CALIBRATION — track {track or 'all'} ({len(names)} concept(s))")
    if not cal["buckets"]:
        print(f"  (no confidence-tagged attempts; {cal['untagged']} untagged)")
        return
    for level in ("sure", "hunch", "no-idea"):
        b = cal["buckets"].get(level)
        if not b:
            continue
        pct = f"{round(100 * b['accuracy'])}%" if b["accuracy"] is not None else "—"
        print(f"  {level:8s} {b['correct']}/{b['n']} correct ({pct})")
    for extra in cal["buckets"]:
        if extra not in ("sure", "hunch", "no-idea"):
            b = cal["buckets"][extra]
            print(f"  {extra:8s} {b['correct']}/{b['n']} correct")
    if cal["flags"]:
        print(f"  flag: {', '.join(cal['flags'])}")
    print(f"  untagged: {cal['untagged']}")


def do_grade_mcq(key: str, answers: str, as_json: bool = False) -> None:
    """Deterministic MCQ grading: per-item pass/fail for an answer key vs answers.

    Comma-separated letters (case-insensitive). An empty or `-` answer is
    unanswered (always wrong). No LLM is involved in the mechanical path."""
    keys = [k.strip().upper() for k in (key or "").split(",")]
    ans = [a.strip().upper() for a in (answers or "").split(",")]
    if not keys or any(not k for k in keys):
        print("GRADE-MCQ FAILED: --key must be a comma list of letters, e.g. A,B,C")
        sys.exit(2)
    if len(keys) != len(ans):
        print(f"GRADE-MCQ FAILED: {len(keys)} key(s) vs {len(ans)} answer(s) — must match")
        sys.exit(2)
    bad = [k for k in keys if not re.fullmatch(r"[A-E]", k)]
    bad += [a for a in ans if a not in ("", "-") and not re.fullmatch(r"[A-E]", a)]
    if bad:
        print(f"GRADE-MCQ FAILED: key/answer tokens must be letters A-E (empty/`-` = unanswered), got {', '.join(sorted(set(bad)))}")
        sys.exit(2)
    items = [
        {"id": i + 1, "key": k, "answer": a if a not in ("", "-") else "—", "pass": a == k}
        for i, (k, a) in enumerate(zip(keys, ans))
    ]
    correct = sum(1 for it in items if it["pass"])
    payload = {"correct": correct, "total": len(items), "items": items}
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    print(f"MCQ GRADE: {correct}/{len(items)} correct")
    for it in items:
        print(f"  {it['id']}. key {it['key']} · answer {it['answer']} → {'PASS' if it['pass'] else 'FAIL'}")


def do_mastery(track: str = "", as_json: bool = False) -> None:
    data, _ = _load_attempts()
    concepts = data.get("concepts", {})
    names = _track_concept_names(concepts, track)
    if not names:
        print("(no concepts)")
        return
    rows = []
    for n in names:
        e = concepts[n]
        rows.append({
            "concept": n,
            "mastery": compute_mastery(e.get("attempts", [])),
            "feynman": e.get("feynman"),
            "next_review": e.get("next_review"),
            "dimensions": compute_dimensions(e),
            "calibration": compute_calibration(e.get("attempts", [])),
            "transfer_ok": transfer_ok(e),
        })
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    for r in rows:
        d = r["dimensions"]
        pretty = " ".join(
            f"{k[:4]} {'—' if v is None else v}"
            for k, v in d.items()
        )
        print(f"{r['concept']} mastery {r['mastery']:.2f} — Feynman: {r['feynman'] or '—'} "
              f"(next {r['next_review']}) | {pretty}")


def _apply_op(kind: str, op: dict) -> str:
    p = _resolve(op["path"])
    if kind == "write":
        p.parent.mkdir(parents=True, exist_ok=True)
        existed = p.exists()
        p.write_text(op["content"], encoding="utf-8")
        return f"{'overwrote' if existed else 'created'} ({len(op['content'])} chars)"
    if kind == "append":
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(op["content"])
        return "appended"
    if kind == "replace":
        text = p.read_text(encoding="utf-8")
        find = op["find"]
        n = text.count(find)
        expected = op.get("count", n)
        if n == 0:
            return "ERROR: find-string not found"
        if expected != 1 and n != expected:
            return f"ERROR: found {n} occurrences, expected {expected}"
        p.write_text(text.replace(find, op["replace_with"], 1) if expected == 1 else text.replace(find, op["replace_with"]), encoding="utf-8")
        return f"replaced {min(n, expected) if expected > 1 else 1} occurrence(s)"


def do_apply(stream) -> None:
    try:
        spec = json.load(stream)
    except json.JSONDecodeError as e:
        print(f"APPLY FAILED: invalid JSON: {e}")
        sys.exit(1)
    results = []
    for kind in ("writes", "appends", "replaces"):
        for op in spec.get(kind, []):
            singular = kind.rstrip("s")
            try:
                res = _apply_op(singular, op)
            except Exception as e:
                res = f"ERROR: {e}"
            results.append((singular, op.get("path"), res))
            print(f"[{singular}] {op.get('path')} -> {res}")
    failed = sum(1 for _, _, r in results if r.startswith("ERROR"))
    print(f"APPLY DONE: {len(results)} op(s), {failed} failed")


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(2)
    cmd, *rest = argv
    if cmd == "bundle":
        do_bundle(*rest)
    elif cmd == "state":
        if not rest:
            print("usage: ops.py state TRACK [--review]")
            sys.exit(2)
        track = next((t for t in rest if not t.startswith("--")), "aiefs")
        if "--review" in rest:
            do_bundle("Learning System/Core/💡 Learning Profile.md")
            do_queue(track, date.today(), 5)
        else:
            do_state(track)
    elif cmd == "queue":
        track = next((t for t in rest if not t.startswith("--")), "aiefs")
        day = date.today()
        slots = 5
        as_json = False
        digest_path = None
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok == "--date" and i + 1 < len(rest):
                parsed = _parse_date(rest[i + 1])
                if parsed is None:
                    print(f"queue: bad --date {rest[i + 1]!r}, want YYYY-MM-DD")
                    sys.exit(2)
                day = parsed; i += 2
            elif tok == "--slots" and i + 1 < len(rest):
                try:
                    slots = max(1, int(rest[i + 1]))
                except ValueError:
                    print(f"queue: bad --slots {rest[i + 1]!r}")
                    sys.exit(2)
                i += 2
            elif tok == "--digest" and i + 1 < len(rest):
                digest_path = rest[i + 1]; i += 2
            elif tok == "--json":
                as_json = True; i += 1
            else:
                i += 1
        do_queue(track, day, slots, as_json=as_json, digest_path=digest_path)
    elif cmd == "apply":
        do_apply(sys.stdin)
    elif cmd == "attempt":
        # attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date D] [--qtype T] [--type C]
        if len(rest) < 2:
            print('usage: ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date YYYY-MM-DD] [--qtype TYPE] [--type C]')
            sys.exit(2)
        concept, result = rest[0], rest[1]
        feynman = qtype = ctype = day = confidence = mode = None
        hints = None
        targets = None
        prereqs = []
        positional = []
        i = 2
        while i < len(rest):
            tok = rest[i]
            if tok == "--date" and i + 1 < len(rest):
                day = rest[i + 1]; i += 2
            elif tok == "--qtype" and i + 1 < len(rest):
                qtype = rest[i + 1]; i += 2
            elif tok == "--type" and i + 1 < len(rest):
                ctype = rest[i + 1]; i += 2
            elif tok == "--confidence" and i + 1 < len(rest):
                confidence = rest[i + 1]; i += 2
            elif tok == "--prereq" and i + 1 < len(rest):
                prereqs.append(rest[i + 1]); i += 2
            elif tok == "--hints" and i + 1 < len(rest):
                try:
                    hints = int(rest[i + 1])
                except ValueError:
                    print(f"ATTEMPT FAILED: --hints must be an integer, got {rest[i + 1]!r}")
                    sys.exit(2)
                i += 2
            elif tok == "--mode" and i + 1 < len(rest):
                mode = rest[i + 1]; i += 2
            elif tok == "--targets" and i + 1 < len(rest):
                targets = rest[i + 1]; i += 2
            else:
                positional.append(tok); i += 1
        if positional:
            feynman = positional[0]
        do_attempt(concept, result, feynman=feynman, date=day, qtype=qtype, ctype=ctype,
                   confidence=confidence, hints=hints, mode=mode, targets=targets,
                   prereqs=prereqs if prereqs else None)
    elif cmd == "grade-mcq":
        key = answers = ""
        as_json = False
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok == "--key" and i + 1 < len(rest):
                key = rest[i + 1]; i += 2
            elif tok == "--answers" and i + 1 < len(rest):
                answers = rest[i + 1]; i += 2
            elif tok == "--json":
                as_json = True; i += 1
            else:
                i += 1
        do_grade_mcq(key, answers, as_json=as_json)
    elif cmd == "prereqs":
        concept = next((t for t in rest if not t.startswith("--")), "")
        if not concept:
            print('usage: ops.py prereqs "Concept" [--set NAME,...] [--json]')
            sys.exit(2)
        set_list = None
        as_json = "--json" in rest
        i = 0
        while i < len(rest):
            if rest[i] == "--set" and i + 1 < len(rest):
                set_list = [p.strip() for p in rest[i + 1].split(",")]
                i += 2
            else:
                i += 1
        do_prereqs(concept, set_list=set_list, as_json=as_json)
    elif cmd == "amend":
        if not rest or rest[0].startswith("--"):
            print('usage: ops.py amend "Concept" --date OLD [--new-date NEW] '
                  '[--field FIELD --value VALUE] --reason "..." [--occurrence N] [--json]')
            sys.exit(2)
        concept = rest[0]
        amend_date = new_date = field = value = reason = None
        occurrence = 1
        as_json = False
        i = 1
        while i < len(rest):
            tok = rest[i]
            if tok == "--date" and i + 1 < len(rest):
                amend_date = rest[i + 1]; i += 2
            elif tok == "--new-date" and i + 1 < len(rest):
                new_date = rest[i + 1]; i += 2
            elif tok == "--field" and i + 1 < len(rest):
                field = rest[i + 1]; i += 2
            elif tok == "--value" and i + 1 < len(rest):
                value = rest[i + 1]; i += 2
            elif tok == "--reason" and i + 1 < len(rest):
                reason = rest[i + 1]; i += 2
            elif tok == "--occurrence" and i + 1 < len(rest):
                try:
                    occurrence = int(rest[i + 1])
                except ValueError:
                    print(f"amend: bad --occurrence {rest[i + 1]!r}")
                    sys.exit(2)
                i += 2
            elif tok == "--json":
                as_json = True; i += 1
            else:
                i += 1
        do_amend(concept, amend_date or "", new_date=new_date, field=field, value=value,
                 reason=reason, occurrence=occurrence, as_json=as_json)
    elif cmd == "calibration":
        as_json = "--json" in rest
        track = next((t for t in rest if not t.startswith("--")), "")
        do_calibration(track, as_json=as_json)
    elif cmd == "mastery":
        as_json = "--json" in rest
        track = next((t for t in rest if not t.startswith("--")), "")
        do_mastery(track, as_json=as_json)
    else:
        print(f"unknown command: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
