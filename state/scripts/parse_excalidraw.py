#!/usr/bin/env python3
"""Reduce an .excalidraw transcription to a GRAPH_CANDIDATES-shaped merge spec.

Mechanical reducer only. Node names and statements stay verbatim from the
drawing's labels; the caller curates statements before any merge. The parser
reads only binding `elementId` fields, so Excalidraw schema drift in focus,
gap, fixedPoint, or mode cannot break the parse.

Nodes come from labelled containers (rectangle, ellipse, diamond) and from
standalone text elements. Chain candidates come only from arrows whose start
and end bindings both resolve to nodes. Arrows with an unbound endpoint get a
geometric fallback (nearest labelled container within --threshold pixels) and
land in notes[] as inferred edges, never as chains.

Rotation is ignored; a rotated arrow's endpoints may be off. Mind-map
transcriptions are written unrotated.

Usage:
  python3 scripts/parse_excalidraw.py <file.excalidraw> [--source PATH]
      [--session NAME] [--threshold PX]

Writes JSON to stdout: {"session", "nodes", "chains", "notes"}.
Exit 0 with at least one node. Exit 2 on invalid input or zero nodes.
"""

import argparse
import json
import sys
from pathlib import Path

CONTAINER_TYPES = {"rectangle", "ellipse", "diamond"}
LINEAR_TYPES = {"arrow", "line"}


def _label_of(element):
    return (element.get("originalText") or element.get("text") or "").strip()


def _bbox_distance(px, py, element):
    x = float(element.get("x") or 0)
    y = float(element.get("y") or 0)
    w = float(element.get("width") or 0)
    h = float(element.get("height") or 0)
    dx = max(x - px, 0.0, px - (x + w))
    dy = max(y - py, 0.0, py - (y + h))
    return (dx * dx + dy * dy) ** 0.5


def _endpoint(element, which):
    points = element.get("points") or []
    if len(points) < 2:
        return None
    point = points[0] if which == "start" else points[-1]
    try:
        return (float(element.get("x") or 0) + float(point[0]),
                float(element.get("y") or 0) + float(point[1]))
    except (TypeError, IndexError):
        return None


def _nearest_node(element, which, elements_by_id, node_index, threshold):
    point = _endpoint(element, which)
    if point is None:
        return None
    best_id, best_dist = None, None
    for eid in node_index:
        dist = _bbox_distance(point[0], point[1], elements_by_id[eid])
        if best_dist is None or dist < best_dist:
            best_id, best_dist = eid, dist
    if best_id is not None and best_dist <= threshold:
        return best_id
    return None


def parse_document(data, *, source, session="mindmap", threshold=80.0):
    """Return {"session","nodes","chains","notes"} for one Excalidraw document."""
    if not isinstance(data, dict) or data.get("type") != "excalidraw":
        raise ValueError("not an excalidraw document")
    elements = [e for e in (data.get("elements") or []) if not e.get("isDeleted")]
    if not elements:
        raise ValueError("no live elements")
    elements_by_id = {e["id"]: e for e in elements if "id" in e}

    labels = {}
    for element in elements:
        if element.get("type") == "text" and element.get("containerId"):
            labels[element["containerId"]] = _label_of(element)

    nodes, node_index, notes = [], {}, []
    for element in elements:
        eid = element.get("id")
        if not eid:
            continue
        if element.get("type") in CONTAINER_TYPES:
            label = labels.get(eid, "")
            if label:
                node_index[eid] = len(nodes)
                nodes.append({"name": label, "statement": label,
                              "provenance": [{"file": source,
                                              "message": "raw mind-map label",
                                              "quote": label}]})
        elif element.get("type") == "text" and not element.get("containerId"):
            label = _label_of(element)
            if label:
                node_index[eid] = len(nodes)
                nodes.append({"name": label, "statement": label,
                              "provenance": [{"file": source,
                                              "message": "raw mind-map label",
                                              "quote": label}]})
    if not nodes:
        raise ValueError("no labeled nodes")

    chains, seen = [], set()
    for element in elements:
        if element.get("type") not in LINEAR_TYPES or not element.get("id"):
            continue
        arrow_id = element["id"]
        start = (element.get("startBinding") or {}).get("elementId")
        end = (element.get("endBinding") or {}).get("elementId")
        if start in node_index and end in node_index:
            key = (start, end)
            if key in seen:
                continue
            seen.add(key)
            a = nodes[node_index[start]]["name"]
            b = nodes[node_index[end]]["name"]
            edge_label = labels.get(arrow_id, "")
            statement = f"{a} {edge_label} {b}" if edge_label else f"{a} leads to {b}"
            chains.append({"premises": [f"@{node_index[start]}"],
                           "conclusion": f"@{node_index[end]}",
                           "statement": statement,
                           "provenance": [{"file": source,
                                           "message": "raw mind-map edge"}]})
            continue
        inferred_start = start if start in node_index else _nearest_node(
            element, "start", elements_by_id, node_index, threshold)
        inferred_end = end if end in node_index else _nearest_node(
            element, "end", elements_by_id, node_index, threshold)
        if inferred_start in node_index and inferred_end in node_index \
                and inferred_start != inferred_end:
            notes.append(
                f"inferred edge '{nodes[node_index[inferred_start]]['name']}' -> "
                f"'{nodes[node_index[inferred_end]]['name']}' from arrow "
                f"'{arrow_id}' (endpoint not bound; not proposed as a chain)")
        else:
            notes.append(
                f"unresolved arrow '{arrow_id}': endpoint not bound and no "
                f"labelled container within {threshold:g}px")

    notes.append("nodes are verbatim mind-map labels; curate statements before merge")
    return {"session": session, "nodes": nodes, "chains": chains, "notes": notes}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Reduce an .excalidraw transcription to a merge spec.")
    parser.add_argument("path", help="path to the .excalidraw file")
    parser.add_argument("--source", default=None,
                        help="provenance file recorded on every record "
                             "(default: the input path)")
    parser.add_argument("--session", default="mindmap")
    parser.add_argument("--threshold", type=float, default=80.0,
                        help="geometric fallback radius in pixels (default 80)")
    args = parser.parse_args(argv)

    try:
        data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"parse_excalidraw: {exc}", file=sys.stderr)
        return 2
    try:
        spec = parse_document(data, source=args.source or args.path,
                              session=args.session, threshold=args.threshold)
    except ValueError as exc:
        print(f"parse_excalidraw: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(spec, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
