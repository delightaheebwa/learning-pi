#!/usr/bin/env python3
"""node_mastery.py — derived per-node evidence view.

Joins three durable stores on every read, and writes nothing:

  Knowledge Wiki/graph/nodes.jsonl + chains.jsonl   subject-matter truth
  Learning System/Core/Attempts.json                reviewed attempts
  Learning System/Core/🧯 Mistakes.md               the mistake ledger

Linking is two-tier. `targets[]` on an attempt and a `[targets: …]` prefix on a
Mistakes row are strict (the ids are explicit). A concept name links strictly
only when it matches exactly one proposition name or alias. Ambiguous concepts
are reported, never attributed, and non-live ids are reported as stale rather
than resolved. Everything else is a fuzzy relevance score for ranking only.

The graph stores world knowledge only (G-graph-world-only). This view is the
learner side of that join: it never writes to the ledgers and never gates a
review. A full `report` is proportional to the ledger (~580 KB at 898 nodes);
prompt consumers should ask for a single node (`--node`) or use `audit`.

Usage:
  node_mastery.py [--root R] report [--json] [--node ID] [--today YYYY-MM-DD]
  node_mastery.py [--root R] audit  [--json] [--today YYYY-MM-DD]
  node_mastery.py [--root R] context --concepts TEXT [--prereq TEXT]
                               [--prior-models FILE] [--out FILE]
                               [--max-bytes N] [--today YYYY-MM-DD]
  node_mastery.py [--root R] drill --node ID [--already ID,ID] [--today YYYY-MM-DD]
  node_mastery.py verify --file FILE
  node_mastery.py verify-envelope --file FILE
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

try:  # run as a script (pi/ is on sys.path) or imported from tests
    import graph
except ModuleNotFoundError:  # pragma: no cover - only when cwd/sys.path differs
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import graph

ATTEMPTS_PATH = Path("Learning System") / "Core" / "Attempts.json"
MISTAKES_PATH = Path("Learning System") / "Core" / "🧯 Mistakes.md"

ERROR_TYPES = {"structural", "deviation", "application", "metacognitive"}
TIERS = ("active", "review", "graduated")
GRADUATED_HALF_LIFE_DAYS = 90

# Presentation budget (bytes of the JSON body, excluding the `budget` object).
BUDGET_BASE_BYTES = 24_000
BUDGET_PER_CONCEPT_BYTES = 4_000
BUDGET_MAX_BYTES = 48_000
INDEX_RESERVE_MAX_BYTES = 8_000
DETAIL_STATEMENT_CHARS = 400
DETAIL_MISTAKE_CHARS = 300
DETAIL_MAX_MISTAKES = 2
DETAIL_MAX_ATTEMPTS = 4
RECENT_FAIL_DAYS = 90
DRILL_MAX_BYTES = 4_096
DRILL_SESSION_MAX = 6

_PREFIX_RE = re.compile(r"^\s*\[(prereq|miss|targets):\s*([^\]]*)\]\s*", re.IGNORECASE)


# ---------------------------------------------------------------------------
# normalization
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Lowercase and collapse everything that is not a letter or digit."""
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _tokens(text: str) -> set[str]:
    return {token for token in _norm(text).split() if len(token) >= 3}


def _targets(value) -> list[str]:
    """Targets are a list in Attempts.json; tolerate a comma/space string."""
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [part for part in re.split(r"[,\s]+", value) if part]
    return []


def _decay(date_text: str, today: date) -> float:
    """90-day half-life for repaired (graduated) evidence."""
    try:
        recorded = date.fromisoformat(str(date_text)[:10])
    except (TypeError, ValueError):
        return 1.0
    age = max(0, (today - recorded).days)
    return round(0.5 ** (age / GRADUATED_HALF_LIFE_DAYS), 3)


# ---------------------------------------------------------------------------
# learners' stores
# ---------------------------------------------------------------------------

def _load_attempts(root: Path) -> dict:
    path = root / ATTEMPTS_PATH
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    concepts = data.get("concepts") if isinstance(data, dict) else None
    return concepts if isinstance(concepts, dict) else {}


def _strip_prefixes(cell: str) -> tuple[str | None, str | None, list[str], str]:
    """Pull `[prereq: …]`, `[miss: …]`, `[targets: …]` off an attribution cell.

    The prefixes are the same convention review-clerk already writes for
    `[prereq:]` and `[miss:]`; unknown brackets and prose are left untouched.
    """
    prereq: str | None = None
    miss_class: str | None = None
    targets: list[str] = []
    text = (cell or "").strip()
    while True:
        match = _PREFIX_RE.match(text)
        if not match:
            break
        key = match.group(1).lower()
        value = match.group(2).strip()
        if key == "prereq":
            prereq = value
        elif key == "miss":
            miss_class = value.lower()
        elif key == "targets":
            targets = [part for part in re.split(r"[,\s]+", value) if part]
        text = text[match.end():]
    return prereq, miss_class, targets, text.strip()


def _load_mistakes(root: Path) -> list[dict]:
    """Parse the Mistakes table with the same anchors as the state-repo parser.

    Rows are located by the error_type cell (cells[4:]) because free-text
    question/expected/attribution cells may themselves contain `|`. Status,
    retries, and next retry are always the last three cells. A short row or one
    with no recognizable error_type is skipped, exactly as `ops.py` does.
    """
    path = root / MISTAKES_PATH
    if not path.is_file():
        return []
    rows: list[dict] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 9:
            continue
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells if cell):
            continue
        if cells[0].lower() == "date":
            continue
        error_index = next(
            (index for index in range(4, len(cells)) if cells[index].lower() in ERROR_TYPES),
            None,
        )
        if error_index is None:
            continue
        prereq, miss_class, targets, attribution = _strip_prefixes(
            " | ".join(cells[error_index + 1:len(cells) - 3])
        )
        rows.append(
            {
                "date": cells[0],
                "concept": cells[1],
                "question": cells[2],
                "expected": " | ".join(cells[3:error_index]),
                "error_type": cells[error_index].lower(),
                "self_attribution": attribution,
                "prereq": prereq,
                "miss_class": miss_class,
                "targets": targets,
                "status": cells[-3].lower(),
                "retries": cells[-2],
                "next_retry": cells[-1],
            }
        )
    return rows


# ---------------------------------------------------------------------------
# join
# ---------------------------------------------------------------------------

def _empty_evidence() -> dict:
    return {
        "attempts": [],
        "fails": 0,
        "last_attempt": None,
        "last_fail": None,
        "mistakes": [],
        "mistake_tiers": {tier: 0 for tier in TIERS},
        "links": {"by_target": 0, "by_chain": 0, "by_concept": 0},
    }


def _attach_attempt_record(target: dict, attempt: dict, link: str) -> None:
    record = {
        "date": attempt.get("date"),
        "result": attempt.get("result"),
        "is_correct": attempt.get("is_correct"),
        "q_type": attempt.get("q_type"),
        "confidence": attempt.get("confidence"),
        "link": link,
    }
    target["attempts"].append(record)
    if record["is_correct"] is False or record["result"] == "fail":
        target["fails"] += 1
        if record["date"] and (target["last_fail"] is None or record["date"] > target["last_fail"]):
            target["last_fail"] = record["date"]
    if record["date"] and (target["last_attempt"] is None or record["date"] > target["last_attempt"]):
        target["last_attempt"] = record["date"]


def _attach_attempt(evidence: dict, attempt: dict, link: str) -> None:
    _attach_attempt_record(evidence, attempt, link)
    key = {"target": "by_target", "chain": "by_chain", "concept": "by_concept"}[link]
    evidence["links"][key] += 1


def _attach_mistake(evidence: dict, mistake: dict, link: str, today: date) -> None:
    status = mistake["status"] if mistake["status"] in TIERS else "active"
    weight = _decay(mistake["date"], today) if status == "graduated" else 1.0
    evidence["mistakes"].append(
        {
            "date": mistake["date"],
            "concept": mistake["concept"],
            "error_type": mistake["error_type"],
            "miss_class": mistake["miss_class"],
            "self_attribution": mistake["self_attribution"],
            "status": status,
            "link": link,
            "weight": weight,
        }
    )
    evidence["mistake_tiers"][status] += 1


def _live_graph(root: Path) -> tuple[dict, dict, dict]:
    ledger = graph.load(root)
    nodes = {
        ident: node
        for ident, node in ledger["nodes"].items()
        if ident not in ledger["retracted_nodes"]
    }
    chains = {
        ident: chain
        for ident, chain in ledger["chains"].items()
        if ident not in ledger["retracted_chains"]
    }
    conclusions = {
        ident: chain["conclusion"] for ident, chain in chains.items()
        if chain["conclusion"] in nodes
    }
    return nodes, chains, conclusions


def _join(root: Path, today: date) -> dict:
    nodes, chains, conclusions = _live_graph(root)
    attempts = _load_attempts(root)
    mistakes = _load_mistakes(root)

    node_evidence = {ident: _empty_evidence() for ident in nodes}
    chain_evidence = {
        ident: {"attempts": [], "fails": 0, "last_attempt": None, "last_fail": None}
        for ident in chains
    }

    # Concept -> node candidates, by exact normalized name or alias.
    node_names: dict[str, set[str]] = {}
    for ident, node in nodes.items():
        labels = {_norm(node.get("name", ""))}
        labels.update(_norm(alias) for alias in node.get("aliases", []) or [])
        for label in labels:
            if label:
                node_names.setdefault(label, set()).add(ident)

    ambiguous: dict[str, list[str]] = {}
    unmatched_concepts: set[str] = set()
    stale_targets: set[str] = set()

    def concept_links(concept: str) -> list[str]:
        matches = sorted(node_names.get(_norm(concept), set()))
        if len(matches) > 1:
            ambiguous[concept] = matches
        elif not matches:
            unmatched_concepts.add(concept)
        return matches

    # Attempts: strict by explicit targets, else by a unique concept match.
    # Concept matching is only consulted when an attempt has no targets, so a
    # fully target-linked concept never shows up as ambiguous or unmatched.
    for concept, entry in attempts.items():
        rows = entry.get("attempts") if isinstance(entry, dict) else None
        for attempt in rows or []:
            if not isinstance(attempt, dict):
                continue
            attached = False
            target_ids = _targets(attempt.get("targets"))
            for target in target_ids:
                if target in nodes:
                    _attach_attempt(node_evidence[target], attempt, "target")
                    attached = True
                elif target in chains:
                    _attach_attempt_record(chain_evidence[target], attempt, "target")
                    conclusion = conclusions.get(target)
                    if conclusion:
                        _attach_attempt(node_evidence[conclusion], attempt, "chain")
                    attached = True
                elif target:
                    # Malformed or non-live: visible as stale, never resolved.
                    stale_targets.add(target)
            if not attached and not target_ids:
                candidates = concept_links(str(concept))
                if len(candidates) == 1:
                    _attach_attempt(node_evidence[candidates[0]], attempt, "concept")

    # Mistakes: strict by `[targets:]`, else by a unique concept match.
    looks_like_mistake: set[str] = set()
    for mistake in mistakes:
        concept = str(mistake["concept"])
        looks_like_mistake.add(concept)
        attached = False
        for target in mistake["targets"]:
            if target in nodes:
                _attach_mistake(node_evidence[target], mistake, "target", today)
                attached = True
            elif target in chains:
                conclusion = conclusions.get(target)
                if conclusion:
                    _attach_mistake(node_evidence[conclusion], mistake, "chain", today)
                    attached = True
                else:
                    stale_targets.add(target)
            else:
                stale_targets.add(target)
        if not attached and not mistake["targets"]:
            candidates = concept_links(concept)
            if len(candidates) == 1:
                _attach_mistake(node_evidence[candidates[0]], mistake, "concept", today)

    # Fuzzy relevance for ranking only: it never attributes evidence.
    relevance = {ident: {"score": 0.0, "concepts": set()} for ident in nodes}
    concept_rows: dict[str, list[dict]] = {}
    for concept, entry in attempts.items():
        for attempt in (entry.get("attempts") if isinstance(entry, dict) else None) or []:
            if isinstance(attempt, dict):
                concept_rows.setdefault(str(concept), []).append(attempt)
    all_concepts = set(concept_rows) | looks_like_mistake
    node_token_sets = {
        ident: _tokens(
            " ".join(
                [node.get("name", ""), node.get("statement", ""),
                 *(node.get("aliases", []) or [])]
            )
        )
        for ident, node in nodes.items()
    }
    for concept in all_concepts:
        concept_tokens = _tokens(concept)
        if not concept_tokens:
            continue
        for ident, node_tokens in node_token_sets.items():
            shared = concept_tokens & node_tokens
            if not shared:
                continue
            relevance[ident]["score"] += len(shared) / max(1, len(concept_tokens))
            relevance[ident]["concepts"].add(concept)

    report_nodes: dict[str, dict] = {}
    for ident in sorted(nodes):
        node = nodes[ident]
        evidence = node_evidence[ident]
        related = relevance[ident]
        evidence["mistakes"].sort(key=lambda row: (row["date"], row["concept"]))
        evidence["attempts"].sort(key=lambda row: (row["date"] or "", row["link"]))
        report_nodes[ident] = {
            "name": node.get("name"),
            "statement": node.get("statement"),
            "aliases": node.get("aliases", []) or [],
            "strict": evidence,
            "related": {
                "score": round(related["score"], 3),
                "concepts": sorted(related["concepts"]),
            },
        }

    report_chains: dict[str, dict] = {}
    for ident in sorted(chains):
        chain = chains[ident]
        report_chains[ident] = {
            "id": ident,
            "premises": chain.get("premises", []),
            "conclusion": chain.get("conclusion"),
            "statement": chain.get("statement", ""),
            "strict": chain_evidence[ident],
        }

    return {
        "as_of": today.isoformat(),
        "graph": {"nodes": len(nodes), "chains": len(chains)},
        "nodes": report_nodes,
        "chains": report_chains,
        "ambiguous": {concept: ids for concept, ids in sorted(ambiguous.items())},
        "stale_targets": sorted(stale_targets),
        "unmatched_concepts": sorted(unmatched_concepts),
        "raw": {"attempts": attempts, "mistakes": mistakes},
    }


# ---------------------------------------------------------------------------
# public views
# ---------------------------------------------------------------------------

def build(root: Path, today: date | None = None, node_id: str | None = None) -> dict:
    view = _join(root, today or date.today())
    view.pop("raw", None)
    if node_id:
        view["nodes"] = {
            ident: record
            for ident, record in view["nodes"].items()
            if ident == node_id
        }
    return view


def audit(root: Path, today: date | None = None) -> dict:
    view = _join(root, today or date.today())
    raw = view.pop("raw")
    nodes = view["nodes"]
    attempts = [
        attempt
        for entry in raw["attempts"].values()
        if isinstance(entry, dict)
        for attempt in entry.get("attempts") or []
        if isinstance(attempt, dict)
    ]
    with_evidence = sum(
        1 for record in nodes.values() if record["strict"]["attempts"] or record["strict"]["mistakes"]
    )
    total = len(nodes)
    tiers = {tier: 0 for tier in TIERS}
    for mistake in raw["mistakes"]:
        tiers[mistake["status"] if mistake["status"] in TIERS else "active"] += 1
    return {
        "as_of": view["as_of"],
        "graph": view["graph"],
        "attempts": {
            "concepts": len(raw["attempts"]),
            "total": len(attempts),
            "with_targets": sum(1 for attempt in attempts if attempt.get("targets")),
        },
        "mistakes": {
            "total": len(raw["mistakes"]),
            "with_targets": sum(1 for mistake in raw["mistakes"] if mistake["targets"]),
            "tiers": tiers,
        },
        "links": {
            "target": sum(record["strict"]["links"]["by_target"] for record in nodes.values()),
            "chain": sum(record["strict"]["links"]["by_chain"] for record in nodes.values()),
            "concept_unique": sum(record["strict"]["links"]["by_concept"] for record in nodes.values()),
            "ambiguous_concepts": len(view["ambiguous"]),
            "stale_targets": len(view["stale_targets"]),
        },
        "coverage": {
            "nodes_with_evidence": with_evidence,
            "nodes_total": total,
            "pct": round(100 * with_evidence / total, 1) if total else 0.0,
        },
        "ambiguous": view["ambiguous"],
        "stale_targets": view["stale_targets"],
        "unmatched_concepts": view["unmatched_concepts"],
    }


# ---------------------------------------------------------------------------
# budgeted prior-knowledge block
# ---------------------------------------------------------------------------

def _json_bytes(value) -> int:
    return len(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _ceiling(concepts: list[str], override: int | None) -> int:
    if override is not None:
        if override <= 0:
            raise graph.GraphError("--max-bytes must be positive")
        return override
    return max(
        BUDGET_BASE_BYTES,
        min(BUDGET_MAX_BYTES, BUDGET_BASE_BYTES + BUDGET_PER_CONCEPT_BYTES * len(concepts)),
    )


def _node_text(node: dict) -> str:
    return " ".join(
        [node.get("name", ""), node.get("statement", ""), *(node.get("aliases", []) or [])]
    )


def _doc_freq(nodes: dict[str, dict]) -> dict[str, int]:
    freq: dict[str, int] = {}
    for record in nodes.values():
        for token in _tokens(_node_text(record)):
            freq[token] = freq.get(token, 0) + 1
    return freq


def _match_quality(text: str, tokens: set[str], concepts: list[str], doc_freq: dict[str, int]) -> float:
    """Rarity-weighted overlap, so `hessian` outranks the ubiquitous `matrix`."""
    best = 0.0
    for concept in concepts:
        normalized = _norm(concept)
        if len(normalized) >= 3 and normalized in text:
            best = max(best, 2.0)
            continue
        concept_tokens = _tokens(concept)
        shared = concept_tokens & tokens
        if not shared:
            continue
        denominator = sum(1.0 / doc_freq.get(token, 1) for token in concept_tokens)
        numerator = sum(1.0 / doc_freq.get(token, 1) for token in shared)
        if denominator:
            best = max(best, 1.5 * numerator / denominator)
    return round(best, 3)


def _node_score(record: dict, node_tokens: set[str], prereq_tokens: set[str], today: date) -> tuple[float, str, int]:
    """Ranking only — never attribution. Higher score plus recency wins."""
    strict = record["strict"]
    links = strict["links"]
    score = 0.0
    if links["by_target"] or links["by_chain"]:
        score += 4.0  # explicit graph ids are the strongest signal
    if links["by_concept"]:
        score += 3.0
    if prereq_tokens & node_tokens:
        score += 1.0
    cutoff = (today - timedelta(days=RECENT_FAIL_DAYS)).isoformat()
    recent_fails = sum(
        1
        for attempt in strict["attempts"]
        if (attempt.get("is_correct") is False or attempt.get("result") == "fail")
        and str(attempt.get("date") or "") >= cutoff
    )
    score += min(2.0, 0.5 * recent_fails)
    open_mistakes = strict["mistake_tiers"]["active"] + strict["mistake_tiers"]["review"]
    if open_mistakes:
        score += 1.0
    score += min(
        1.0,
        sum(row["weight"] for row in strict["mistakes"] if row["status"] == "graduated"),
    )
    dates = [str(attempt.get("date") or "") for attempt in strict["attempts"]]
    dates += [row["date"] for row in strict["mistakes"]]
    return round(score, 3), max(dates) if dates else "", open_mistakes


def _detail(ident: str, record: dict) -> dict:
    strict = record["strict"]
    attempts = sorted(
        strict["attempts"], key=lambda row: str(row.get("date") or ""), reverse=True
    )[:DETAIL_MAX_ATTEMPTS]
    mistakes = sorted(strict["mistakes"], key=lambda row: row["date"], reverse=True)
    mistakes.sort(key=lambda row: row["status"] == "graduated")  # open/review first
    mistakes = [
        {
            "date": row["date"],
            "concept": row["concept"],
            "error_type": row["error_type"],
            "miss_class": row["miss_class"],
            "status": row["status"],
            "self_attribution": row["self_attribution"][:DETAIL_MISTAKE_CHARS],
            "link": row["link"],
            "weight": row["weight"],
        }
        for row in mistakes[:DETAIL_MAX_MISTAKES]
    ]
    return {
        "id": ident,
        "name": record["name"],
        "statement": str(record["statement"] or "")[:DETAIL_STATEMENT_CHARS],
        "attempts": attempts,
        "fails": strict["fails"],
        "last_attempt": strict["last_attempt"],
        "last_fail": strict["last_fail"],
        "mistakes": mistakes,
        "links": strict["links"],
        "score": record.get("_score", 0.0),
    }


def _assemble(
    as_of: str,
    propositions: list[dict],
    chains: list[dict],
    index: list[dict],
    omitted: dict,
    prior_models: list[dict] | None = None,
) -> dict:
    mistakes = [
        {"node": prop["id"], **row}
        for prop in propositions
        for row in prop["mistakes"]
    ]
    return {
        "as_of": as_of,
        "propositions": propositions,
        "chains": chains,
        "mistakes": mistakes,
        "prior_models": prior_models or [],
        "index": index,
        "omitted": omitted,
    }


def build_context(
    root: Path,
    concepts: list[str],
    prereqs: list[str] | None = None,
    today: date | None = None,
    max_bytes: int | None = None,
    prior_models: list[dict] | None = None,
) -> dict:
    """Budgeted `prior_knowledge` block: complete index + scored detail."""
    today = today or date.today()
    concepts = list(dict.fromkeys(
        term.strip() for term in concepts if term and term.strip()
    ))
    if not concepts:
        raise graph.GraphError("context needs at least one --concepts term")
    prereqs = [term.strip() for term in (prereqs or []) if term and term.strip()]
    ceiling = _ceiling(concepts, max_bytes)

    view = build(root, today)
    terms = [_norm(term) for term in [*concepts, *prereqs] if _norm(term)]
    term_tokens = set().union(*(_tokens(term) for term in [*concepts, *prereqs]))
    prereq_tokens = set().union(*(_tokens(term) for term in prereqs)) if prereqs else set()

    doc_freq = _doc_freq(view["nodes"])
    matched: list[dict] = []
    for ident, record in view["nodes"].items():
        text = _norm(_node_text(record))
        tokens = _tokens(_node_text(record))
        explicit = record["strict"]["links"]["by_target"] or record["strict"]["links"]["by_chain"]
        hit = any(len(term) >= 3 and term in text for term in terms) or bool(term_tokens & tokens)
        if not hit and not explicit:
            continue
        score, last_date, open_mistakes = _node_score(record, tokens, prereq_tokens, today)
        score = round(
            score + _match_quality(text, tokens, concepts, doc_freq), 3
        )
        record["_score"] = score
        matched.append(
            {
                "id": ident,
                "record": record,
                "score": score,
                "last_date": last_date,
                "open_mistakes": open_mistakes,
            }
        )

    # Deterministic, score-first ordering: id, then date desc, then score desc.
    matched.sort(key=lambda row: row["id"])
    matched.sort(key=lambda row: row["last_date"] or "", reverse=True)
    matched.sort(key=lambda row: row["score"], reverse=True)

    index = [
        {
            "id": row["id"],
            "name": row["record"]["name"],
            "attempts": len(row["record"]["strict"]["attempts"]),
            "fails": row["record"]["strict"]["fails"],
            "open_mistakes": row["open_mistakes"],
            "last_fail": row["record"]["strict"]["last_fail"],
            "score": row["score"],
        }
        for row in matched
    ]

    # Index reserve: enough for the full index when the ceiling has room,
    # capped at a third of the budget; overflow is visible in `omitted`.
    reserve = min(INDEX_RESERVE_MAX_BYTES, max(2_000, ceiling // 3))
    index_kept = list(index)
    index_dropped = 0
    while index_kept and _json_bytes(index_kept) > reserve:
        index_kept.pop()
        index_dropped += 1

    omitted = {
        "index": index_dropped,
        "propositions": 0,
        "chains": 0,
        "mistakes": 0,
        "reason": "budget" if index_dropped else "",
        "next_best": [],
    }
    propositions: list[dict] = []
    chain_candidates: list[dict] = []
    detail_ids: set[str] = set()

    body = _assemble(today.isoformat(), propositions, chain_candidates, index_kept, omitted, prior_models)

    indexed_ids = {entry["id"] for entry in index_kept}
    for candidate in matched:
        if candidate["id"] not in indexed_ids:
            continue
        entry = _detail(candidate["id"], candidate["record"])
        trial = _assemble(
            today.isoformat(), propositions + [entry], chain_candidates, index_kept, omitted, prior_models
        )
        if _json_bytes(trial) > ceiling:
            break
        propositions.append(entry)
        detail_ids.add(candidate["id"])

    # Chains only when every endpoint is in the detail set.
    for chain in view["chains"].values():
        if chain.get("conclusion") not in detail_ids:
            continue
        if not all(premise in detail_ids for premise in chain.get("premises", [])):
            continue
        entry = {
            "id": chain["id"],
            "premises": chain.get("premises", []),
            "conclusion": chain.get("conclusion"),
            "statement": chain.get("statement", ""),
        }
        trial = _assemble(
            today.isoformat(), propositions, chain_candidates + [entry], index_kept, omitted, prior_models
        )
        if _json_bytes(trial) > ceiling:
            break
        chain_candidates.append(entry)

    omitted["propositions"] = len(matched) - len(propositions)
    omitted["chains"] = sum(
        1
        for chain in view["chains"].values()
        if chain.get("conclusion") in detail_ids
        and all(premise in detail_ids for premise in chain.get("premises", []))
    ) - len(chain_candidates)
    omitted["mistakes"] = sum(
        len(row["record"]["strict"]["mistakes"]) for row in matched
    ) - sum(len(prop["mistakes"]) for prop in propositions)
    omitted["next_best"] = [row["id"] for row in matched if row["id"] not in detail_ids][:5]
    if omitted["chains"] < 0:
        omitted["chains"] = 0
    if omitted["mistakes"] < 0:
        omitted["mistakes"] = 0

    body = _assemble(today.isoformat(), propositions, chain_candidates, index_kept, omitted, prior_models)
    body = _sweep(body, index_kept, ceiling, omitted, today.isoformat(), prior_models)
    total_mistakes = sum(len(row["record"]["strict"]["mistakes"]) for row in matched)
    omitted["mistakes"] = max(
        0, total_mistakes - sum(len(prop["mistakes"]) for prop in body["propositions"])
    )
    if any(omitted[key] for key in ("index", "propositions", "chains")):
        omitted["reason"] = "budget"
    elif omitted["mistakes"]:
        omitted["reason"] = "detail-caps"
    else:
        omitted["reason"] = ""

    body_bytes = _json_bytes(body)
    if body_bytes > ceiling:
        raise graph.GraphError(
            f"cannot fit prior knowledge in {ceiling} bytes (need at least {body_bytes}); "
            "raise --max-bytes"
        )

    result = dict(body)
    result["budget"] = {
        "ceiling_bytes": ceiling,
        "body_bytes": body_bytes,
        "estimator": "json-utf8-bytes",
        "matched_nodes": len(matched),
        "detail_nodes": len(result["propositions"]),
        "index_nodes": len(result["index"]),
    }
    return result


def _sweep(
    body: dict,
    index_kept: list[dict],
    ceiling: int,
    omitted: dict,
    as_of: str,
    prior_models: list[dict] | None,
) -> dict:
    """Keep the block coherent and under the ceiling.

    Drops propositions whose index line went away, drops chains with a dropped
    endpoint, then sheds units until the ceiling holds. Bounded by the unit
    count, so it always terminates.
    """
    for _ in range(
        len(body["propositions"]) + len(body["chains"]) + len(index_kept) + 8
    ):
        kept_index_ids = {entry["id"] for entry in index_kept}
        survivors = [prop for prop in body["propositions"] if prop["id"] in kept_index_ids]
        survivor_ids = {prop["id"] for prop in survivors}
        chains_kept = [
            chain
            for chain in body["chains"]
            if chain.get("conclusion") in survivor_ids
            and isinstance(chain.get("premises"), list)
            and all(premise in survivor_ids for premise in chain["premises"])
        ]
        if survivors != body["propositions"] or chains_kept != body["chains"]:
            dropped = [prop["id"] for prop in body["propositions"] if prop["id"] not in survivor_ids]
            omitted["propositions"] += len(body["propositions"]) - len(survivors)
            omitted["chains"] += len(body["chains"]) - len(chains_kept)
            omitted["next_best"] = (dropped + omitted["next_best"])[:5]
            body = _assemble(as_of, survivors, chains_kept, index_kept, omitted, prior_models)
            continue
        if _json_bytes(body) <= ceiling:
            break
        if body["propositions"]:
            dropped = body["propositions"].pop()
            omitted["propositions"] += 1
            omitted["next_best"] = ([dropped["id"]] + omitted["next_best"])[:5]
        elif body["chains"]:
            body["chains"].pop()
            omitted["chains"] += 1
        elif index_kept:
            index_kept.pop()
            omitted["index"] += 1
        else:
            break
        body = _assemble(
            as_of, body["propositions"], body["chains"], index_kept, omitted, prior_models
        )
    return body


def drill_node(
    root: Path,
    node_id: str,
    today: date | None = None,
    already: list[str] | None = None,
    max_bytes: int = DRILL_MAX_BYTES,
) -> dict:
    """One node record for the tail the digest omitted, capped at 4 KB.

    Stateless: the caller passes the ids it already drilled (`--already`) and
    the envelope carries the cumulative list, so no per-session file is needed.
    """
    already = [item.strip() for item in (already or []) if item and item.strip()]
    if len(already) >= DRILL_SESSION_MAX:
        raise graph.GraphError(
            f"DRILL_BUDGET_EXHAUSTED: {len(already)} drills already used "
            f"(max {DRILL_SESSION_MAX} per session)"
        )
    view = build(root, today)
    record = view["nodes"].get(node_id)
    if not record:
        raise graph.GraphError(f"unknown node {node_id}")
    entry = _detail(node_id, dict(record))

    truncated = False
    if _json_bytes(entry) > max_bytes:
        truncated = True
        entry["mistakes"] = entry["mistakes"][:1]
        while entry["mistakes"] and _json_bytes(entry) > max_bytes:
            entry["mistakes"].pop()
        if _json_bytes(entry) > max_bytes:
            entry["statement"] = entry["statement"][:200]
        if _json_bytes(entry) > max_bytes:
            entry["statement"] = entry["statement"][:80]
        if _json_bytes(entry) > max_bytes:
            entry["attempts"] = []
        if _json_bytes(entry) > max_bytes:
            entry["links"] = {}
        if _json_bytes(entry) > max_bytes:
            raise graph.GraphError(
                f"cannot fit the drill record in {max_bytes} bytes"
            )

    entry["origin"] = "drilldown"
    return {
        "origin": "drilldown",
        "node": entry,
        "truncated": truncated,
        "bytes": _json_bytes(entry),
        "session": {
            "drilled": len(already) + 1,
            "remaining": DRILL_SESSION_MAX - len(already) - 1,
        },
    }


def verify_envelope(path: Path) -> dict:
    """Check the cited prior-knowledge subset a fact-check envelope carries."""
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"file": str(path), "ok": False, "errors": [f"unreadable: {exc}"]}
    if not isinstance(data, dict):
        return {"file": str(path), "ok": False, "errors": ["not a JSON object"]}

    prior = data.get("prior_knowledge")
    if not isinstance(prior, dict):
        errors.append("prior_knowledge must be an object")
        drills = []
    else:
        drills = prior.get("drilldown", [])
        if not isinstance(drills, list):
            errors.append("prior_knowledge.drilldown must be a list")
            drills = []
    if len(drills) > DRILL_SESSION_MAX:
        errors.append(f"{len(drills)} drilldown records exceeds {DRILL_SESSION_MAX} per session")

    seen: set[str] = set()
    total_bytes = 0
    for index, drill in enumerate(drills):
        if not isinstance(drill, dict):
            errors.append(f"drilldown[{index}] is not an object")
            continue
        if drill.get("origin") != "drilldown":
            errors.append(f"drilldown[{index}] is missing origin:drilldown")
        node = drill.get("node") if isinstance(drill.get("node"), dict) else {}
        ident = node.get("id")
        if not isinstance(ident, str) or not _shape_ok(ident):
            errors.append(f"drilldown[{index}] has no graph-shaped node id")
        elif ident in seen:
            errors.append(f"drilldown[{index}] duplicates {ident}")
        else:
            seen.add(ident)
        if not node.get("statement"):
            errors.append(f"drilldown[{index}] has no statement")
        size = _json_bytes(drill)
        total_bytes += size
        if size > DRILL_MAX_BYTES:
            errors.append(f"drilldown[{index}] is {size} bytes (max {DRILL_MAX_BYTES})")
    if total_bytes > DRILL_SESSION_MAX * DRILL_MAX_BYTES:
        errors.append(f"drilldown total {total_bytes} bytes exceeds the session allowance")

    return {
        "file": str(path),
        "drills": len(drills),
        "drill_bytes": total_bytes,
        "ok": not errors,
        "errors": errors,
    }


def _shape_ok(ident: str) -> bool:
    return bool(re.fullmatch(r"(?:n|arg)_[a-z0-9]{6,}", ident))


def verify_block(path: Path) -> dict:
    """Structural verification: schema, budget arithmetic, index coverage.

    Liveness is deliberately NOT re-checked here; ids were live when the block
    was generated and `ops.py` still checks liveness at record time. A
    concurrent ingest must not invalidate a digest mid-session.
    """
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"file": str(path), "ok": False, "errors": [f"unreadable: {exc}"]}
    if not isinstance(data, dict):
        return {"file": str(path), "ok": False, "errors": ["not a JSON object"]}

    required = {"as_of", "propositions", "chains", "mistakes", "prior_models", "index", "omitted", "budget"}
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"missing keys: {missing}")

    budget = data.get("budget") if isinstance(data.get("budget"), dict) else {}
    body = {key: value for key, value in data.items() if key != "budget"}
    actual = _json_bytes(body)
    if budget.get("body_bytes") != actual:
        errors.append(f"budget.body_bytes {budget.get('body_bytes')} != actual {actual}")
    ceiling = budget.get("ceiling_bytes")
    if not isinstance(ceiling, int) or actual > ceiling:
        errors.append(f"body {actual} exceeds ceiling {ceiling}")

    index = data.get("index") if isinstance(data.get("index"), list) else []
    index_ids = [entry.get("id") for entry in index if isinstance(entry, dict)]
    if len(index_ids) != len(set(index_ids)):
        errors.append("duplicate ids in index")
    propositions = data.get("propositions") if isinstance(data.get("propositions"), list) else []
    prop_ids = [entry.get("id") for entry in propositions if isinstance(entry, dict)]
    if len(prop_ids) != len(set(prop_ids)):
        errors.append("duplicate ids in propositions")
    missing_from_index = [ident for ident in prop_ids if ident not in set(index_ids)]
    if missing_from_index:
        errors.append(f"propositions missing from index: {missing_from_index}")

    detail_ids = set(prop_ids)
    chains = data.get("chains") if isinstance(data.get("chains"), list) else []
    for chain in chains:
        if not isinstance(chain, dict):
            errors.append("chain entry is not an object")
            continue
        premises = chain.get("premises")
        if not isinstance(premises, list):
            errors.append(f"chain {chain.get('id')} premises must be a list")
            continue
        endpoints = list(premises) + [chain.get("conclusion")]
        if any(endpoint not in detail_ids for endpoint in endpoints):
            errors.append(f"chain {chain.get('id')} has an endpoint outside the retained detail")

    mistakes = data.get("mistakes") if isinstance(data.get("mistakes"), list) else []
    orphan_mistakes = [
        row.get("node") for row in mistakes
        if isinstance(row, dict) and row.get("node") not in set(prop_ids)
    ]
    if orphan_mistakes:
        errors.append(f"mistakes attached to omitted propositions: {orphan_mistakes}")

    if not isinstance(data.get("prior_models"), list):
        errors.append("prior_models must be a list")
    omitted = data.get("omitted") if isinstance(data.get("omitted"), dict) else {}
    for key in ("index", "propositions", "chains", "mistakes"):
        value = omitted.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"omitted.{key} must be a non-negative integer")

    return {
        "file": str(path),
        "body_bytes": actual,
        "ceiling_bytes": ceiling,
        "ok": not errors,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _today(text: str | None) -> date:
    if not text:
        return date.today()
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise graph.GraphError(f"--today must be YYYY-MM-DD: {exc}") from exc


def _print_report(view: dict) -> None:
    for ident, record in view["nodes"].items():
        strict = record["strict"]
        print(
            f"{ident} — {record['name']}: attempts={len(strict['attempts'])} "
            f"fails={strict['fails']} mistakes={len(strict['mistakes'])} "
            f"related={record['related']['score']}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="derived per-node evidence view")
    parser.add_argument("--root", default=None, help="learning-system checkout (default: detect)")
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report", help="per-node evidence and relevance")
    report.add_argument("--json", action="store_true")
    report.add_argument("--node", default=None, help="only this graph id")
    report.add_argument("--today", default=None, help="YYYY-MM-DD (deterministic decay)")

    audit_cmd = sub.add_parser("audit", help="coverage, ambiguity, stale ids")
    audit_cmd.add_argument("--json", action="store_true")
    audit_cmd.add_argument("--today", default=None, help="YYYY-MM-DD (deterministic decay)")

    context = sub.add_parser(
        "context", help="budgeted prior_knowledge block (complete index + scored detail)"
    )
    context.add_argument(
        "--concepts",
        action="append",
        default=[],
        help="lesson/review concept terms (repeatable, comma-separated)",
    )
    context.add_argument(
        "--prereq", action="append", default=[], help="prereq terms that boost matching nodes"
    )
    context.add_argument(
        "--prior-models",
        default=None,
        help="JSON array of verbatim prior models to include inside the budget",
    )
    context.add_argument("--out", default=None, help="write the block here (else stdout)")
    context.add_argument("--max-bytes", type=int, default=None, help="ceiling override (bytes)")
    context.add_argument("--today", default=None, help="YYYY-MM-DD (deterministic decay)")

    verify_cmd = sub.add_parser("verify", help="structural check of a generated block")
    verify_cmd.add_argument("--file", required=True)
    verify_cmd.add_argument("--json", action="store_true")

    drill = sub.add_parser("drill", help="one omitted node record (<=4 KB, <=6/session)")
    drill.add_argument("--node", required=True)
    drill.add_argument(
        "--already",
        default="",
        help="comma-separated ids already drilled this session (cumulative cap)",
    )
    drill.add_argument("--today", default=None, help="YYYY-MM-DD (deterministic decay)")

    envelope = sub.add_parser("verify-envelope", help="check the cited drilldown subset")
    envelope.add_argument("--file", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            receipt = verify_block(Path(args.file))
            prefix = "PRIOR_BUDGET_OK: " if receipt["ok"] else "PRIOR_BUDGET_FAILED: "
            print(prefix + json.dumps(receipt, ensure_ascii=False, sort_keys=True))
            return 0 if receipt["ok"] else 1
        if args.command == "verify-envelope":
            receipt = verify_envelope(Path(args.file))
            prefix = "DRILL_BUDGET_OK: " if receipt["ok"] else "DRILL_BUDGET_FAILED: "
            print(prefix + json.dumps(receipt, ensure_ascii=False, sort_keys=True))
            return 0 if receipt["ok"] else 1
        root = graph.resolve_root(args.root)
        today = _today(args.today)
        if args.command == "drill":
            record = drill_node(
                root,
                args.node,
                today,
                already=[part for part in args.already.split(",") if part.strip()],
            )
            print("DRILL_RECORD: " + json.dumps(record, ensure_ascii=False, sort_keys=True))
            print("DRILL_SPEND: " + json.dumps(record["session"], sort_keys=True))
            return 0
        if args.command == "context":
            terms = [term for value in args.concepts for term in value.split(",")]
            prior_models = None
            if args.prior_models:
                try:
                    prior_models = json.loads(Path(args.prior_models).read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise graph.GraphError(f"--prior-models unreadable: {exc}") from exc
                if not isinstance(prior_models, list):
                    raise graph.GraphError("--prior-models must be a JSON array")
            block = build_context(
                root, terms, args.prereq, today, args.max_bytes, prior_models=prior_models
            )
            payload = json.dumps(block, ensure_ascii=False, indent=2, sort_keys=True)
            if args.out:
                path = Path(args.out)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(payload + "\n", encoding="utf-8")
                receipt = {
                    "file": args.out,
                    "ceiling_bytes": block["budget"]["ceiling_bytes"],
                    "body_bytes": block["budget"]["body_bytes"],
                    "detail": len(block["propositions"]),
                    "index": len(block["index"]),
                    "omitted": block["omitted"],
                }
                print("PRIOR_CONTEXT: " + json.dumps(receipt, ensure_ascii=False, sort_keys=True))
            else:
                print(payload)
            return 0
        if args.command == "report":
            view = build(root, today, args.node)
            if args.json:
                print(json.dumps(view, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                _print_report(view)
            return 0
        if args.command == "audit":
            result = audit(root, today)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(
                    f"nodes={result['graph']['nodes']} attempts={result['attempts']['total']} "
                    f"(with targets {result['attempts']['with_targets']}) "
                    f"mistakes={result['mistakes']['total']} "
                    f"strict evidence on {result['coverage']['nodes_with_evidence']} nodes "
                    f"({result['coverage']['pct']}%)"
                )
                if result["ambiguous"]:
                    print(f"ambiguous concepts: {len(result['ambiguous'])}")
                if result["stale_targets"]:
                    print(f"stale targets: {len(result['stale_targets'])}")
            return 0
    except graph.GraphError as exc:
        print(f"NODE_MASTERY FAILED: {exc}")
        return 1
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
