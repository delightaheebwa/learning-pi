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
review.

Usage:
  node_mastery.py [--root R] report [--json] [--node ID] [--today YYYY-MM-DD]
  node_mastery.py [--root R] audit  [--json] [--today YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
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

_ID_RE = re.compile(r"^(?:n|arg)_[a-z0-9]{6,}$")
_PREFIX_RE = re.compile(r"^\s*\[(prereq|miss|targets):\s*([^\]]*)\]\s*", re.IGNORECASE)


# ---------------------------------------------------------------------------
# normalization
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Lowercase and collapse everything that is not a letter or digit."""
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _tokens(text: str) -> set[str]:
    return {token for token in _norm(text).split() if len(token) >= 3}


def _valid_id(value: str) -> bool:
    return bool(_ID_RE.match(value.strip()))


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
                "targets": [target for target in targets if _valid_id(target)],
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
    for concept, entry in attempts.items():
        candidates = concept_links(str(concept))
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
                elif _valid_id(target):
                    stale_targets.add(target)
                # Malformed ids are ignored: they can never be graph records.
            if not attached and not target_ids and len(candidates) == 1:
                _attach_attempt(node_evidence[candidates[0]], attempt, "concept")

    # Mistakes: strict by `[targets:]`, else by a unique concept match.
    looks_like_mistake: set[str] = set()
    for mistake in mistakes:
        concept = str(mistake["concept"])
        looks_like_mistake.add(concept)
        candidates = concept_links(concept)
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
        if not attached and not mistake["targets"] and len(candidates) == 1:
            _attach_mistake(node_evidence[candidates[0]], mistake, "concept", today)

    # Fuzzy relevance for ranking only: it never attributes evidence.
    relevance = {ident: {"score": 0.0, "concepts": set()} for ident in nodes}
    concept_rows: dict[str, list[dict]] = {}
    for concept, entry in attempts.items():
        for attempt in (entry.get("attempts") if isinstance(entry, dict) else None) or []:
            if isinstance(attempt, dict):
                concept_rows.setdefault(str(concept), []).append(attempt)
    all_concepts = set(concept_rows) | looks_like_mistake
    for concept in all_concepts:
        concept_tokens = _tokens(concept)
        if not concept_tokens:
            continue
        for ident, node in nodes.items():
            node_tokens = _tokens(
                " ".join(
                    [node.get("name", ""), node.get("statement", ""),
                     *(node.get("aliases", []) or [])]
                )
            )
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
            "premises": chain.get("premises", []),
            "conclusion": chain.get("conclusion"),
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = graph.resolve_root(args.root)
        today = _today(args.today)
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
