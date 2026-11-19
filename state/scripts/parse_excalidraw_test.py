#!/usr/bin/env python3
"""Tests for scripts/parse_excalidraw.py — stdlib only.

Covers the parser contract from docs/plans/solo-first-implementation.md (Task 1):
labelled shapes and standalone text become nodes, fully bound arrows become
chain candidates, and geometric fallbacks stay in notes[] as inferred edges.
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_excalidraw  # noqa: E402

NODE_FIELDS = {"name", "statement", "aliases", "provenance", "link_to"}
CHAIN_FIELDS = {"premises", "conclusion", "statement", "provenance"}


def _doc(elements):
    return {"type": "excalidraw", "version": 2, "elements": elements}


def _rect(eid, x=0, y=0, width=100, height=50):
    return {"id": eid, "type": "rectangle", "x": x, "y": y,
            "width": width, "height": height}


def _text(eid, text, container=None, original=None):
    return {"id": eid, "type": "text", "x": 0, "y": 0, "width": 10, "height": 10,
            "text": text, "originalText": original if original is not None else text,
            "containerId": container}


def _arrow(eid, start=None, end=None, x=0, y=0, points=None):
    return {"id": eid, "type": "arrow", "x": x, "y": y, "width": 10, "height": 10,
            "points": points if points is not None else [[0, 0], [10, 0]],
            "startBinding": {"elementId": start} if start else None,
            "endBinding": {"elementId": end} if end else None}


class TestNodes(unittest.TestCase):
    def test_labelled_shape_becomes_a_node(self):
        doc = _doc([
            _rect("r1"),
            _text("t1", "Causality", container="r1"),
        ])
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual([n["name"] for n in spec["nodes"]], ["Causality"])
        self.assertEqual([n["statement"] for n in spec["nodes"]], ["Causality"])

    def test_standalone_text_becomes_a_node(self):
        doc = _doc([_text("t1", "Attention")])
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual([n["name"] for n in spec["nodes"]], ["Attention"])

    def test_arrow_bound_text_is_an_edge_label_not_a_node(self):
        doc = _doc([
            _rect("r1"), _rect("r2", x=300),
            _text("t1", "A", container="r1"), _text("t2", "B", container="r2"),
            _arrow("a1", start="r1", end="r2"),
            _text("t3", "causes", container="a1"),
        ])
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual([n["name"] for n in spec["nodes"]], ["A", "B"])
        self.assertIn("causes", spec["chains"][0]["statement"])

    def test_original_text_wins_over_wrapped_text(self):
        doc = _doc([
            _rect("r1"),
            _text("t1", "Causality\nis the", container="r1",
                  original="Causality is the study"),
        ])
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual(spec["nodes"][0]["name"], "Causality is the study")

    def test_deleted_elements_are_skipped(self):
        deleted = _rect("r1")
        deleted["isDeleted"] = True
        doc = _doc([deleted, _text("t1", "x", container="r1"), _text("t2", "Live")])
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual([n["name"] for n in spec["nodes"]], ["Live"])


class TestEdges(unittest.TestCase):
    def _two_node_doc(self, arrow):
        return _doc([
            _rect("r1"), _rect("r2", x=300),
            _text("t1", "A", container="r1"), _text("t2", "B", container="r2"),
            arrow,
        ])

    def test_fully_bound_arrow_becomes_a_chain_candidate(self):
        doc = self._two_node_doc(_arrow("a1", start="r1", end="r2"))
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual(len(spec["chains"]), 1)
        chain = spec["chains"][0]
        self.assertEqual(chain["premises"], ["@0"])
        self.assertEqual(chain["conclusion"], "@1")
        self.assertIn("A", chain["statement"])
        self.assertIn("B", chain["statement"])
        self.assertEqual(chain["provenance"][0]["file"], "note.md")

    def test_half_bound_arrow_goes_to_notes_not_chains(self):
        # Endpoint at (300, 0) is 300px from r2's edge, so widen the threshold.
        doc = self._two_node_doc(
            _arrow("a1", start="r1", points=[[0, 0], [380, 0]]))
        spec = parse_excalidraw.parse_document(
            doc, source="note.md", threshold=400)
        self.assertEqual(spec["chains"], [])
        self.assertTrue(any("inferred" in note for note in spec["notes"]))

    def test_unbound_arrow_far_from_nodes_is_unresolved(self):
        doc = self._two_node_doc(
            _arrow("a1", points=[[0, 500], [10, 500]]))
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual(spec["chains"], [])
        self.assertTrue(any("unresolved" in note for note in spec["notes"]))

    def test_duplicate_arrows_collapse_to_one_chain(self):
        doc = self._two_node_doc(_arrow("a1", start="r1", end="r2"))
        doc["elements"].append(_arrow("a2", start="r1", end="r2"))
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        self.assertEqual(len(spec["chains"]), 1)


class TestErrors(unittest.TestCase):
    def test_non_excalidraw_document_raises(self):
        with self.assertRaises(ValueError):
            parse_excalidraw.parse_document({"type": "other"}, source="note.md")

    def test_empty_elements_raise(self):
        with self.assertRaises(ValueError):
            parse_excalidraw.parse_document(_doc([]), source="note.md")

    def test_zip_without_labels_raises(self):
        with self.assertRaises(ValueError):
            parse_excalidraw.parse_document(
                _doc([_rect("r1")]), source="note.md")


class TestMergeShape(unittest.TestCase):
    def test_records_use_only_merge_legal_fields(self):
        doc = _doc([
            _rect("r1"), _rect("r2", x=300),
            _text("t1", "A", container="r1"), _text("t2", "B", container="r2"),
            _arrow("a1", start="r1", end="r2"),
        ])
        spec = parse_excalidraw.parse_document(doc, source="note.md")
        for node in spec["nodes"]:
            self.assertLessEqual(set(node), NODE_FIELDS)
        for chain in spec["chains"]:
            self.assertLessEqual(set(chain), CHAIN_FIELDS)
        self.assertIsInstance(spec["notes"], list)
        self.assertIn("session", spec)


class TestCli(unittest.TestCase):
    def _run(self, doc, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.excalidraw"
            path.write_text(json.dumps(doc), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = parse_excalidraw.main([str(path), *extra])
            return code, out.getvalue(), err.getvalue()

    def test_valid_file_exits_zero_and_emits_json(self):
        code, out, _ = self._run(_doc([_text("t1", "Attention")]))
        self.assertEqual(code, 0)
        spec = json.loads(out)
        self.assertEqual(spec["nodes"][0]["name"], "Attention")

    def test_source_flag_sets_provenance(self):
        code, out, _ = self._run(
            _doc([_text("t1", "Attention")]), "--source", "note.md")
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out)["nodes"][0]["provenance"][0]["file"], "note.md")

    def test_invalid_json_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.excalidraw"
            path.write_text("{not json", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = parse_excalidraw.main([str(path)])
            self.assertEqual(code, 2)
            self.assertIn("parse_excalidraw", err.getvalue())


if __name__ == "__main__":
    unittest.main()
