#!/usr/bin/env python3
"""
graph.py — the learning-system knowledge graph: propositions + reasoning chains.

Stored truth (append-only JSONL under `Knowledge Wiki/graph/`):
  nodes.jsonl   propositions. One line per assertion: op `define` creates,
                op `link` records a re-encounter (verbatim alias + provenance),
                op `retract` tombstones an id.
  chains.jsonl  reasoning chains. One line per argument: a premise set that
                jointly implies a conclusion, with provenance.

Edges are NEVER stored. The rendered graph is a derived, lossy view: each chain
mints an implication node (premises -> ⟹ -> conclusion), so two independent
arguments for one conclusion stay two diamonds instead of a manufactured fan-in.

Sole writer: `merge` (and `retract`). Agents never hand-write the ledgers; the
Clerk runs the merge. The graph holds subject-matter claims only — never learner
state (mastery, verdicts, confidence, understanding, grades). That evidence
lives in Attempts.json / 🧯 Mistakes.md. Unknown fields are rejected precisely so
learner-state keys cannot enter the graph by accident.

Usage:
  graph.py [--root R] status  [--json]
  graph.py [--root R] list    [--json] [--session ID]
  graph.py [--root R] merge   < spec.json
  graph.py [--root R] retract <id> --reason TEXT
  graph.py [--root R] export  [--json | --mermaid]

Merge spec (stdin):
  {"session": "<id>",                       # optional; fills provenance.session
   "nodes": [
     {"name": "...", "statement": "...",    # new proposition (id is derived from
      "aliases": ["..."],                   # the normalized statement, so the
      "provenance": [{"file": "...",        # merge is idempotent)
                      "message": "..."}]},
     {"link_to": "n_ab12cd34ef",            # re-encounter of an existing one
      "statement": "verbatim phrasing", "provenance": [...]}
   ],
   "chains": [
     {"premises": ["@0", "n_ab12cd34ef"],   # @N = nodes[N] from this spec
      "conclusion": "@1", "statement": "A ∧ B ⟹ C", "provenance": [...]}
   ]}

Root resolution: --root, else $LEARNING_SYSTEM_ROOT, else ~/learning-system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

GRAPH_DIR = "Knowledge Wiki/graph"
NODES_FILE = "nodes.jsonl"
CHAINS_FILE = "chains.jsonl"

NODE_FIELDS = {
    "id", "op", "name", "statement", "aliases", "provenance", "link_to", "createdAt", "reason",
}
CHAIN_FIELDS = {
    "id", "op", "premises", "conclusion", "statement", "provenance", "createdAt", "reason",
}
PROVENANCE_FIELDS = {"file", "session", "message", "quote", "heading", "url"}
ID_RE = re.compile(r"^(n|arg)_[a-z0-9]{6,}$")

# Fields that are legal in the learning system but must never enter the graph.
LEARNER_STATE_FIELDS = {
    "mastery", "confidence", "verdict", "verdicts", "correct", "is_correct",
    "result", "pass", "fail", "passed", "failed", "grade", "grades", "score",
    "understanding", "learner_model", "learner", "attempt", "attempts",
    "assessment", "level", "feynman", "review", "next_review", "status",
}

NODES_HEADER = "# nodes — propositions (one JSON object per line). See README.md.\n"
CHAINS_HEADER = "# chains — reasoning chains: premises jointly imply conclusion. See README.md.\n"


class GraphError(Exception):
    """A validation or integrity failure. Nothing is written when raised."""


# ---------------------------------------------------------------------------
# ids and normalization
# ---------------------------------------------------------------------------

def normalize_statement(statement: str) -> str:
    return re.sub(r"\s+", " ", (statement or "").strip().lower())


def node_id(statement: str) -> str:
    """Deterministic, content-addressed id: re-asserting a statement links it."""
    digest = hashlib.sha256(normalize_statement(statement).encode("utf-8")).hexdigest()
    return "n_" + digest[:10]


def chain_fingerprint(premises: list[str], conclusion: str) -> str:
    body = "\n".join(sorted(set(premises))) + "\n=>\n" + conclusion
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def chain_id(premises: list[str], conclusion: str) -> str:
    return "arg_" + chain_fingerprint(premises, conclusion)[:10]


# ---------------------------------------------------------------------------
# root resolution and IO
# ---------------------------------------------------------------------------

def resolve_root(explicit: str | None) -> Path:
    candidates = [
        explicit or "",
        os.environ.get("LEARNING_SYSTEM_ROOT", ""),
        os.path.expanduser("~/learning-system"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser().resolve()
        if (path / "Learning System" / "Core").is_dir():
            return path
    raise GraphError(
        "no learning-system checkout found (need 'Learning System/Core'); pass --root"
    )


def graph_dir(root: Path) -> Path:
    return root / GRAPH_DIR


def _read_jsonl(path: Path) -> list[tuple[int, dict | None]]:
    """Yield (line_number, record) pairs; record None marks a malformed line."""
    if not path.is_file():
        return []
    out: list[tuple[int, dict | None]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            record = json.loads(line)
            out.append((number, record if isinstance(record, dict) else None))
        except json.JSONDecodeError:
            out.append((number, None))
    return out


def _append_line(path: Path, record: dict, header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(header, encoding="utf-8")
    body = json.dumps(record, ensure_ascii=False, sort_keys=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(body + "\n")


def _dedupe_points(points: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for point in points:
        key = json.dumps(point, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(point)
    return out


# ---------------------------------------------------------------------------
# load (reader side merges the append-only ledgers)
# ---------------------------------------------------------------------------

def load(root: Path) -> dict:
    """Read and merge both ledgers. Never raises for malformed data; reports it."""
    gdir = graph_dir(root)
    nodes: dict[str, dict] = {}
    chains: dict[str, dict] = {}
    chain_by_fingerprint: dict[str, str] = {}
    retracted_nodes: dict[str, str] = {}
    retracted_chains: dict[str, str] = {}
    problems: list[str] = []

    for number, record in _read_jsonl(gdir / NODES_FILE):
        if record is None:
            problems.append(f"{NODES_FILE}:{number}: malformed JSON line")
            continue
        ident = record.get("id")
        op = record.get("op", "define")
        if not isinstance(ident, str) or not ID_RE.fullmatch(ident):
            problems.append(f"{NODES_FILE}:{number}: missing/invalid id")
            continue
        if set(record) - NODE_FIELDS:
            problems.append(
                f"{NODES_FILE}:{number}: unknown field(s) {sorted(set(record) - NODE_FIELDS)}"
            )
        if op == "retract":
            retracted_nodes[ident] = str(record.get("reason", ""))
            continue
        if op not in ("define", "link"):
            problems.append(f"{NODES_FILE}:{number}: unknown op {op!r}")
            continue
        if op == "link":
            existing = nodes.get(ident)
            if existing is None:
                problems.append(f"{NODES_FILE}:{number}: link before define for {ident}")
                continue
            statement = str(record.get("statement", "")).strip()
            if statement and statement not in existing["aliases"]:
                existing["aliases"].append(statement)
            for alias in record.get("aliases", []) or []:
                alias = str(alias).strip()
                if alias and alias not in existing["aliases"]:
                    existing["aliases"].append(alias)
            existing["provenance"] = _dedupe_points(
                existing["provenance"] + list(record.get("provenance", []) or [])
            )
            continue
        if ident in nodes:
            problems.append(f"{NODES_FILE}:{number}: duplicate define for {ident}")
            continue
        nodes[ident] = {
            "id": ident,
            "name": str(record.get("name", "")).strip(),
            "statement": str(record.get("statement", "")).strip(),
            "aliases": [str(a).strip() for a in record.get("aliases", []) or [] if str(a).strip()],
            "provenance": _dedupe_points(list(record.get("provenance", []) or [])),
            "createdAt": str(record.get("createdAt", "")),
        }

    for number, record in _read_jsonl(gdir / CHAINS_FILE):
        if record is None:
            problems.append(f"{CHAINS_FILE}:{number}: malformed JSON line")
            continue
        ident = record.get("id")
        op = record.get("op", "assert")
        if set(record) - CHAIN_FIELDS:
            problems.append(
                f"{CHAINS_FILE}:{number}: unknown field(s) {sorted(set(record) - CHAIN_FIELDS)}"
            )
        if op == "retract":
            if isinstance(ident, str):
                retracted_chains[ident] = str(record.get("reason", ""))
            else:
                problems.append(f"{CHAINS_FILE}:{number}: retract without id")
            continue
        if op != "assert":
            problems.append(f"{CHAINS_FILE}:{number}: unknown op {op!r}")
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
            problems.append(f"{CHAINS_FILE}:{number}: chain needs premises[] + conclusion")
            continue
        fingerprint = chain_fingerprint(premises, conclusion)
        if fingerprint in chain_by_fingerprint:
            existing = chains[chain_by_fingerprint[fingerprint]]
            existing["provenance"] = _dedupe_points(
                existing["provenance"] + list(record.get("provenance", []) or [])
            )
            continue
        resolved_id = ident if isinstance(ident, str) and ID_RE.fullmatch(ident) else chain_id(
            premises, conclusion
        )
        chains[resolved_id] = {
            "id": resolved_id,
            "premises": sorted(set(premises)),
            "conclusion": conclusion,
            "statement": str(record.get("statement", "")).strip(),
            "provenance": _dedupe_points(list(record.get("provenance", []) or [])),
            "createdAt": str(record.get("createdAt", "")),
        }
        chain_by_fingerprint[fingerprint] = resolved_id

    return {
        "nodes": nodes,
        "chains": chains,
        "retracted_nodes": retracted_nodes,
        "retracted_chains": retracted_chains,
        "problems": problems,
    }


def _live_nodes(graph: dict) -> dict[str, dict]:
    return {
        ident: node
        for ident, node in graph["nodes"].items()
        if ident not in graph["retracted_nodes"]
    }


def _live_chains(graph: dict) -> list[dict]:
    return [
        chain
        for chain in graph["chains"].values()
        if chain["id"] not in graph["retracted_chains"]
    ]


def integrity(graph: dict) -> dict:
    """Classify chain references: dropped (deliberate retraction) vs dangling (bad)."""
    live = _live_nodes(graph)
    dropped: list[dict] = []
    dangling: list[dict] = []
    for chain in _live_chains(graph):
        missing = [
            ident
            for ident in [*chain["premises"], chain["conclusion"]]
            if ident not in live
        ]
        if not missing:
            continue
        if all(ident in graph["retracted_nodes"] for ident in missing):
            dropped.append({**chain, "dropped_for": missing})
        else:
            dangling.append({**chain, "missing": missing})
    return {"dropped": dropped, "dangling": dangling}


def derived(root: Path) -> dict:
    """The rendered graph: live propositions + chains as implication nodes."""
    graph = load(root)
    live = _live_nodes(graph)
    verdict = integrity(graph)
    dropped_ids = {chain["id"] for chain in verdict["dropped"]}
    dangling_ids = {chain["id"] for chain in verdict["dangling"]}

    nodes_out = [
        {
            "id": ident,
            "kind": "proposition",
            "name": node["name"],
            "statement": node["statement"],
            "aliases": node["aliases"],
            "provenance": node["provenance"],
        }
        for ident, node in live.items()
    ]
    edges: list[dict] = []
    for chain in _live_chains(graph):
        if chain["id"] in dropped_ids or chain["id"] in dangling_ids:
            continue
        premises = "; ".join(live[p]["name"] or live[p]["statement"] for p in chain["premises"])
        conclusion = live[chain["conclusion"]]["name"]
        nodes_out.append(
            {
                "id": chain["id"],
                "kind": "implication",
                "name": "⟹",
                "statement": chain["statement"]
                or f"{premises} ⟹ {conclusion}",
                "provenance": chain["provenance"],
            }
        )
        for premise in chain["premises"]:
            edges.append({"from": premise, "to": chain["id"]})
        edges.append({"from": chain["id"], "to": chain["conclusion"]})
    return {
        "nodes": nodes_out,
        "edges": edges,
        "dropped_chains": len(verdict["dropped"]),
        "dangling_chains": len(verdict["dangling"]),
        "problems": graph["problems"],
    }


# ---------------------------------------------------------------------------
# validation (nothing is written unless the whole spec validates)
# ---------------------------------------------------------------------------

def _check_keys(record: dict, allowed: set[str], where: str) -> None:
    extra = set(record) - allowed
    if not extra:
        return
    learner = sorted(extra & LEARNER_STATE_FIELDS)
    if learner:
        raise GraphError(
            f"{where}: field(s) {learner} look like learner state — the graph stores "
            "subject-matter propositions only. Learner evidence belongs in "
            "Attempts.json / 🧯 Mistakes.md."
        )
    raise GraphError(f"{where}: unknown field(s) {sorted(extra)} (allowed: {sorted(allowed)})")


def _with_session(point, session: str | None):
    """Add the spec's session id to a provenance point that lacks one."""
    if isinstance(point, dict) and session and "session" not in point:
        return {**point, "session": session}
    return point


def _check_provenance(points, where: str) -> list[dict]:
    if not isinstance(points, list) or not points:
        raise GraphError(f"{where}: provenance is required (list of file/session/message points)")
    clean: list[dict] = []
    for point in points:
        if not isinstance(point, dict):
            raise GraphError(f"{where}: each provenance point must be an object")
        _check_keys(point, PROVENANCE_FIELDS, f"{where}.provenance")
        if not any(
            isinstance(point.get(key), str) and point[key].strip()
            for key in ("file", "session")
        ):
            raise GraphError(f"{where}: each provenance point needs a non-empty `file` or `session`")
        clean.append({k: str(v).strip() for k, v in point.items() if isinstance(v, str) and v.strip()})
    return clean


def plan_merge(graph: dict, spec: dict, session: str | None = None) -> dict:
    """Resolve a spec into concrete records without writing anything."""
    if not isinstance(spec, dict):
        raise GraphError("merge spec must be a JSON object")
    _check_keys(spec, {"session", "nodes", "chains"}, "spec")
    raw_nodes = spec.get("nodes", []) or []
    raw_chains = spec.get("chains", []) or []
    if not isinstance(raw_nodes, list) or not isinstance(raw_chains, list):
        raise GraphError("spec.nodes and spec.chains must be lists")
    session = session or spec.get("session")
    session = session.strip() if isinstance(session, str) else None

    live = _live_nodes(graph)
    created_nodes: list[dict] = []
    linked_nodes: list[dict] = []
    resolved: list[str] = []
    node_records: list[dict] = []

    for index, raw in enumerate(raw_nodes):
        where = f"nodes[{index}]"
        if not isinstance(raw, dict):
            raise GraphError(f"{where}: must be an object")
        _check_keys(raw, NODE_FIELDS, where)
        provenance = _check_provenance(
            [_with_session(point, session) for point in raw.get("provenance", [])],
            where,
        )
        if raw.get("link_to"):
            target = str(raw["link_to"])
            if target not in live and target not in {n["id"] for n in created_nodes}:
                raise GraphError(f"{where}: link_to {target} is not a live proposition")
            statement = str(raw.get("statement", "")).strip()
            if not statement:
                raise GraphError(f"{where}: a link needs the verbatim statement it re-encounters")
            record = {
                "id": target,
                "op": "link",
                "statement": statement,
                "aliases": [str(a).strip() for a in raw.get("aliases", []) or [] if str(a).strip()],
                "provenance": provenance,
            }
            node_records.append(record)
            linked_nodes.append(record)
            resolved.append(target)
            continue

        name = str(raw.get("name", "")).strip()
        statement = str(raw.get("statement", "")).strip()
        if not name:
            raise GraphError(f"{where}: `name` is required (a short label)")
        if not statement:
            raise GraphError(f"{where}: `statement` is required (one self-contained proposition)")
        ident = node_id(statement)
        already_created = {record["id"] for record in created_nodes}
        if ident in live or ident in already_created:
            record = {
                "id": ident,
                "op": "link",
                "statement": statement,
                "aliases": [str(a).strip() for a in raw.get("aliases", []) or [] if str(a).strip()],
                "provenance": provenance,
            }
            linked_nodes.append(record)
            node_records.append(record)
        else:
            record = {
                "id": ident,
                "op": "define",
                "name": name,
                "statement": statement,
                "aliases": [str(a).strip() for a in raw.get("aliases", []) or [] if str(a).strip()],
                "provenance": provenance,
            }
            created_nodes.append(record)
            node_records.append(record)
        resolved.append(ident)

    known = set(live) | {record["id"] for record in node_records}
    created_chains: list[dict] = []
    linked_chains: list[dict] = []
    chain_records: list[dict] = []
    existing_fingerprints = {
        chain_fingerprint(chain["premises"], chain["conclusion"]): chain["id"]
        for chain in _live_chains(graph)
    }
    for index, raw in enumerate(raw_chains):
        where = f"chains[{index}]"
        if not isinstance(raw, dict):
            raise GraphError(f"{where}: must be an object")
        _check_keys(raw, CHAIN_FIELDS, where)
        provenance = _check_provenance(
            [_with_session(point, session) for point in raw.get("provenance", [])],
            where,
        )

        def resolve_ref(ref) -> str:
            ref = str(ref).strip()
            if ref.startswith("@"):
                try:
                    return resolved[int(ref[1:])]
                except (ValueError, IndexError):
                    raise GraphError(f"{where}: {ref} does not point at a node in this spec")
            if ref not in known:
                raise GraphError(f"{where}: unknown premise/conclusion id {ref}")
            return ref

        premises = [resolve_ref(ref) for ref in (raw.get("premises") or [])]
        if not premises:
            raise GraphError(f"{where}: a chain needs at least one premise")
        conclusion = resolve_ref(raw.get("conclusion") or "")
        if not conclusion:
            raise GraphError(f"{where}: a chain needs a conclusion")
        if conclusion in premises:
            raise GraphError(f"{where}: the conclusion cannot also be a premise")
        fingerprint = chain_fingerprint(premises, conclusion)
        record = {
            "premises": sorted(set(premises)),
            "conclusion": conclusion,
            "statement": str(raw.get("statement", "")).strip(),
            "provenance": provenance,
        }
        if fingerprint in existing_fingerprints:
            record["id"] = existing_fingerprints[fingerprint]
            record["op"] = "assert"
            linked_chains.append(record)
        else:
            record["id"] = chain_id(premises, conclusion)
            record["op"] = "assert"
            created_chains.append(record)
        chain_records.append(record)

    return {
        "node_records": node_records,
        "chain_records": chain_records,
        "created_nodes": created_nodes,
        "linked_nodes": linked_nodes,
        "created_chains": created_chains,
        "linked_chains": linked_chains,
        "resolved": resolved,
    }


def apply_merge(root: Path, plan: dict) -> dict:
    gdir = graph_dir(root)
    stamp = _now()
    for record in plan["node_records"]:
        _append_line(
            gdir / NODES_FILE,
            {**record, "createdAt": stamp},
            NODES_HEADER,
        )
    for record in plan["chain_records"]:
        _append_line(
            gdir / CHAINS_FILE,
            {**record, "createdAt": stamp},
            CHAINS_HEADER,
        )
    return {
        "nodes_created": len(plan["created_nodes"]),
        "nodes_linked": len(plan["linked_nodes"]),
        "chains_created": len(plan["created_chains"]),
        "chains_linked": len(plan["linked_chains"]),
        "node_ids": [record["id"] for record in plan["created_nodes"]],
        "chain_ids": [record["id"] for record in plan["created_chains"]],
    }


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def cmd_status(root: Path, as_json: bool) -> int:
    graph = load(root)
    verdict = integrity(graph)
    status = {
        "nodes": len(_live_nodes(graph)),
        "chains": len(_live_chains(graph)),
        "retracted_nodes": len(graph["retracted_nodes"]),
        "retracted_chains": len(graph["retracted_chains"]),
        "dropped_chains": len(verdict["dropped"]),
        "dangling_chains": len(verdict["dangling"]),
        "problems": len(graph["problems"]),
    }
    failed = bool(graph["problems"] or verdict["dangling"])
    if as_json:
        print(json.dumps({**status, "details": {
            "problems": graph["problems"],
            "dangling": [
                {"id": chain["id"], "missing": chain["missing"]}
                for chain in verdict["dangling"]
            ],
        }}, ensure_ascii=False, indent=2))
    else:
        print(
            f"graph: {status['nodes']} propositions, {status['chains']} chains "
            f"({status['retracted_nodes']} retracted nodes, {status['dropped_chains']} dropped chains)"
        )
        for problem in graph["problems"]:
            print(f"ERROR {problem}")
        for chain in verdict["dangling"]:
            print(f"ERROR dangling chain {chain['id']} (missing {chain['missing']})")
    print(
        "GRAPH_STATUS: "
        + json.dumps({**status, "ok": not failed}, ensure_ascii=False, sort_keys=True)
    )
    return 1 if failed else 0


def cmd_list(root: Path, as_json: bool, session: str | None) -> int:
    graph = load(root)
    live = _live_nodes(graph)
    if session:
        live = {
            ident: node
            for ident, node in live.items()
            if any(point.get("session") == session for point in node["provenance"])
        }
    nodes = list(live.values())
    chains = [
        chain
        for chain in _live_chains(graph)
        if not session or chain["conclusion"] in live
    ]
    if as_json:
        print(
            json.dumps(
                {
                    "nodes": nodes,
                    "chains": chains,
                    "retracted_nodes": len(graph["retracted_nodes"]),
                    "problems": graph["problems"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1 if graph["problems"] else 0
    for node in nodes:
        print(f"{node['id']} — {node['name']}: {node['statement']}")
    for chain in chains:
        premise_names = [
            (live[p]["name"] if p in live else p) for p in chain["premises"]
        ]
        conclusion = live[chain["conclusion"]]["name"] if chain["conclusion"] in live else chain["conclusion"]
        print(f"{chain['id']} — {' ∧ '.join(premise_names)} ⟹ {conclusion}")
    if not nodes and not chains:
        print("(empty graph)")
    return 1 if graph["problems"] else 0


def cmd_merge(root: Path, stream) -> int:
    try:
        spec = json.load(stream)
    except json.JSONDecodeError as exc:
        print(f"GRAPH_MERGE FAILED: invalid JSON: {exc}")
        return 1
    graph = load(root)
    try:
        plan = plan_merge(graph, spec)
    except GraphError as exc:
        print(f"GRAPH_MERGE FAILED: {exc}")
        return 1
    receipt = apply_merge(root, plan)
    print("GRAPH_MERGE: " + json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_retract(root: Path, ident: str, reason: str) -> int:
    graph = load(root)
    gdir = graph_dir(root)
    if ident in graph["nodes"]:
        _append_line(
            gdir / NODES_FILE,
            {"id": ident, "op": "retract", "reason": reason, "createdAt": _now()},
            NODES_HEADER,
        )
        kind = "node"
    elif ident in graph["chains"]:
        _append_line(
            gdir / CHAINS_FILE,
            {"id": ident, "op": "retract", "reason": reason, "createdAt": _now()},
            CHAINS_HEADER,
        )
        kind = "chain"
    else:
        print(f"GRAPH_RETRACT FAILED: no node or chain with id {ident}")
        return 1
    print(
        "GRAPH_RETRACT: "
        + json.dumps({"id": ident, "kind": kind, "reason": reason}, ensure_ascii=False, sort_keys=True)
    )
    return 0


def _mermaid_label(text: str) -> str:
    return re.sub(r'["\r\n]+', "'", text).strip() or "?"


def cmd_export(root: Path, as_json: bool) -> int:
    view = derived(root)
    if as_json:
        print(json.dumps(view, ensure_ascii=False, indent=2))
        return 1 if view["problems"] else 0
    print("graph TD")
    for node in view["nodes"]:
        label = _mermaid_label(
            f"{node['name']}: {node['statement']}" if node["kind"] == "proposition" else "⟹"
        )
        shape = "{{" if node["kind"] == "implication" else "["
        close = "}}" if node["kind"] == "implication" else "]"
        print(f'  {node["id"]}{shape}"{label}"{close}')
    for edge in view["edges"]:
        print(f"  {edge['from']} --> {edge['to']}")
    return 1 if view["problems"] else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="learning-system knowledge graph CLI")
    parser.add_argument("--root", default=None, help="learning-system checkout (default: detect)")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="integrity/counts")
    status.add_argument("--json", action="store_true")

    listing = sub.add_parser("list", help="list propositions and chains")
    listing.add_argument("--json", action="store_true")
    listing.add_argument("--session", default=None, help="only nodes touched by this session")

    sub.add_parser("merge", help="deterministically merge a candidate spec from stdin")

    retract = sub.add_parser("retract", help="tombstone a node or chain (cascades in the view)")
    retract.add_argument("id")
    retract.add_argument("--reason", required=True)

    export = sub.add_parser("export", help="derived view (mermaid by default)")
    export.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        root = resolve_root(args.root)
    except GraphError as exc:
        print(f"GRAPH FAILED: {exc}")
        return 2

    try:
        if args.command == "status":
            return cmd_status(root, args.json)
        if args.command == "list":
            return cmd_list(root, args.json, args.session)
        if args.command == "merge":
            return cmd_merge(root, sys.stdin)
        if args.command == "retract":
            return cmd_retract(root, args.id, args.reason)
        if args.command == "export":
            return cmd_export(root, args.json)
    except GraphError as exc:
        print(f"GRAPH FAILED: {exc}")
        return 1
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
