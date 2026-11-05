#!/usr/bin/env python3
"""End-to-end Hessian walkthrough for the derived per-node pipeline.

Builds a synthetic learner history (graph + targeted fail + active and
repaired mistakes), generates the budgeted `prior_knowledge` block, checks
that the attack-relevant evidence is inside it, drills the omitted tail, and
proves the graph ledgers are untouched.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYER = HERE.parent.parent
sys.path.insert(0, str(LAYER / "pi"))

import node_mastery  # noqa: E402

graph = node_mastery.graph
TODAY = date(2026, 11, 5)

HESSIAN = "The Hessian is symmetric when second partials are continuous."
DEFINITENESS = "Hessian definiteness classifies critical points."
SECOND_PARTIALS = "The Hessian is the matrix of second partials."
JACOBIAN = "The Jacobian stacks first partials."


def prov(path: str = "Learning System/Lessons/eigenvalues.md") -> dict:
    return {"file": path}


class HessianEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.core = self.root / "Learning System" / "Core"
        self.core.mkdir(parents=True)

        self.merge({
            "nodes": [
                {"name": "Hessian symmetry", "statement": HESSIAN,
                 "aliases": ["Hessian matrix"], "provenance": [prov()]},
                {"name": "Hessian definiteness", "statement": DEFINITENESS,
                 "provenance": [prov()]},
                {"name": "Hessian as second partials", "statement": SECOND_PARTIALS,
                 "provenance": [prov()]},
                {"name": "Jacobian rows", "statement": JACOBIAN, "provenance": [prov()]},
            ],
            "chains": [
                {"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]},
            ],
        })
        self.hessian_id = graph.node_id(HESSIAN)

        self.write_attempts({
            "Hessian matrix": {
                "type": "concept",
                "attempts": [
                    {
                        "date": "2026-10-30",
                        "is_correct": False,
                        "result": "fail",
                        "q_type": "transfer-near",
                        "confidence": "hunch",
                        "targets": [self.hessian_id],
                    }
                ],
            }
        })
        self.write_mistakes([
            {
                "date": "2026-10-30",
                "concept": "Hessian matrix",
                "error_type": "application",
                "self_attribution": "[miss: discrimination] [targets: "
                + self.hessian_id
                + "] I treated PSD as sufficient for a strict minimum",
                "status": "active",
            },
            {
                "date": "2026-11-04",
                "concept": "Hessian matrix",
                "error_type": "structural",
                "self_attribution": "[miss: structural] repaired symmetry vs definiteness",
                "status": "graduated",
            },
        ])
        self.models = [
            {
                "concept": "Hessian matrix",
                "version": "v2",
                "words": "The Hessian tells me the curvature; symmetry is about mixed partials",
                "file": "Learning System/Lessons/eigenvalues.md",
            }
        ]

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- helpers -----------------------------------------------------------
    def merge(self, spec: dict) -> dict:
        return graph.apply_merge(self.root, graph.plan_merge(graph.load(self.root), spec))

    def write_attempts(self, concepts: dict) -> None:
        (self.core / "Attempts.json").write_text(
            json.dumps({"concepts": concepts, "meta": {"version": 1, "intervals": {}}}),
            encoding="utf-8",
        )

    def write_mistakes(self, rows: list[dict]) -> None:
        lines = [
            "| Date | Concept | Question | Expected | Error Type | Self-Attribution | Status | Retries | Next Retry |\n",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n",
        ]
        for row in rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["date"], row["concept"], "q | extra", "e | extra", row["error_type"],
                        row["self_attribution"], row["status"], "0", "2026-12-01",
                    ]
                )
                + " |\n"
            )
        (self.core / "🧯 Mistakes.md").write_text("".join(lines), encoding="utf-8")

    def block(self, max_bytes: int = 12_000) -> dict:
        return node_mastery.build_context(
            self.root,
            ["Hessian matrix"],
            today=TODAY,
            max_bytes=max_bytes,
            prior_models=self.models,
        )

    # -- the walkthrough ---------------------------------------------------
    def test_hessian_block_carries_the_seam_and_the_struggle(self) -> None:
        block = self.block()
        self.assertLessEqual(block["budget"]["body_bytes"], block["budget"]["ceiling_bytes"])
        receipt = node_mastery.verify_block(self._block_path(block))
        self.assertTrue(receipt["ok"], receipt["errors"])

        index_ids = {entry["id"] for entry in block["index"]}
        self.assertIn(self.hessian_id, index_ids)
        self.assertNotIn(graph.node_id(JACOBIAN), index_ids)

        prop = next(p for p in block["propositions"] if p["id"] == self.hessian_id)
        self.assertEqual(prop["attempts"][0]["link"], "target")
        active = next(row for row in prop["mistakes"] if row["status"] == "active")
        graduated = next(row for row in prop["mistakes"] if row["status"] == "graduated")
        self.assertEqual(active["link"], "target")
        self.assertEqual(graduated["link"], "concept")
        self.assertEqual(active["miss_class"], "discrimination")
        self.assertIn("PSD as sufficient", active["self_attribution"])
        self.assertEqual(active["weight"], 1.0)
        self.assertAlmostEqual(graduated["weight"], 0.992, places=3)
        self.assertEqual(block["prior_models"][0]["words"], self.models[0]["words"])

        audit = node_mastery.audit(self.root, TODAY)
        self.assertEqual(audit["attempts"]["with_targets"], 1)
        self.assertEqual(audit["links"]["target"], 1)
        self.assertGreaterEqual(audit["coverage"]["nodes_with_evidence"], 1)
        self.assertEqual(audit["mistakes"]["tiers"]["active"], 1)
        self.assertEqual(audit["mistakes"]["tiers"]["graduated"], 1)

    def test_hessian_tail_is_drillable_and_verifiable(self) -> None:
        block = self.block(max_bytes=800)
        self.assertGreater(block["omitted"]["propositions"], 0)
        target = block["omitted"]["next_best"][0]
        record = node_mastery.drill_node(self.root, target, TODAY)
        self.assertLessEqual(node_mastery._json_bytes(record), node_mastery.DRILL_MAX_BYTES)
        envelope = self.root / ".tmp" / "envelope.json"
        envelope.parent.mkdir(parents=True, exist_ok=True)
        envelope.write_text(json.dumps({"prior_knowledge": {"drilldown": [record]}}))
        envelope_receipt = node_mastery.verify_envelope(envelope)
        self.assertTrue(envelope_receipt["ok"], envelope_receipt["errors"])

    def test_hessian_report_is_deterministic_and_read_only(self) -> None:
        before = (
            (self.root / graph.GRAPH_DIR / graph.NODES_FILE).read_bytes(),
            (self.root / graph.GRAPH_DIR / graph.CHAINS_FILE).read_bytes(),
            (self.core / "Attempts.json").read_bytes(),
            (self.core / "🧯 Mistakes.md").read_bytes(),
        )
        first = json.dumps(self.block(), sort_keys=True)
        second = json.dumps(self.block(), sort_keys=True)
        self.assertEqual(first, second)
        after = (
            (self.root / graph.GRAPH_DIR / graph.NODES_FILE).read_bytes(),
            (self.root / graph.GRAPH_DIR / graph.CHAINS_FILE).read_bytes(),
            (self.core / "Attempts.json").read_bytes(),
            (self.core / "🧯 Mistakes.md").read_bytes(),
        )
        self.assertEqual(before, after)

    def _block_path(self, block: dict) -> Path:
        path = self.root / ".tmp" / "prior.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(block), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
