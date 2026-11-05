#!/usr/bin/env python3
"""Behavior tests for pi/node_mastery.py — the derived per-node evidence view.

Temp roots only: no learning system, no graph writes. The view must stay
read-only, keep ambiguous concepts out of attribution, and never drop
graduated (repaired) mistakes.
"""

from __future__ import annotations

import contextlib
import io
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


def prov(path: str = "Learning System/Lessons/lesson.md", **extra) -> dict:
    return {"file": path, **extra}


class NodeMasteryCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.core = self.root / "Learning System" / "Core"
        self.core.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- helpers -----------------------------------------------------------
    def merge(self, spec: dict) -> dict:
        return graph.apply_merge(self.root, graph.plan_merge(graph.load(self.root), spec))

    def seed(self, *nodes: dict) -> None:
        self.merge({"nodes": [{"provenance": [prov()], **node} for node in nodes]})

    def write_attempts(self, concepts: dict) -> None:
        (self.core / "Attempts.json").write_text(
            json.dumps({"concepts": concepts, "meta": {"version": 1, "intervals": {}}}),
            encoding="utf-8",
        )

    def write_mistakes(self, rows: list[dict]) -> None:
        header = (
            "# Mistakes\n\n## Table\n\n"
            "| Date | Concept | Question | Expected | Error Type | Self-Attribution | Status | Retries | Next Retry |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        )
        lines = [header]
        for row in rows:
            cells = [
                row["date"],
                row["concept"],
                row.get("question", "q"),
                row.get("expected", "e"),
                row["error_type"],
                row.get("self_attribution", "why"),
                row.get("status", "active"),
                str(row.get("retries", 0)),
                row.get("next_retry", "2026-12-01"),
            ]
            lines.append("| " + " | ".join(cells) + " |\n")
        (self.core / "🧯 Mistakes.md").write_text("".join(lines), encoding="utf-8")

    def attempt(self, concept: str, *, targets=None, correct=False, recorded="2026-10-30") -> dict:
        entry = {
            "date": recorded,
            "is_correct": correct,
            "result": "pass" if correct else "fail",
            "q_type": "transfer-near",
        }
        if targets:
            entry["targets"] = targets
        return {concept: {"type": "concept", "attempts": [entry]}}

    def state_bytes(self) -> tuple[bytes, ...]:
        nodes = self.root / graph.GRAPH_DIR / graph.NODES_FILE
        chains = self.root / graph.GRAPH_DIR / graph.CHAINS_FILE
        attempts = self.core / "Attempts.json"
        mistakes = self.core / "🧯 Mistakes.md"
        paths = (nodes, chains, attempts, mistakes)
        return tuple(path.read_bytes() if path.is_file() else b"" for path in paths)

    # -- read-only ---------------------------------------------------------
    def test_report_leaves_the_graph_ledgers_untouched(self) -> None:
        statement = "The Hessian is symmetric when second partials are continuous."
        self.seed({"name": "Hessian symmetry", "statement": statement})
        ident = graph.node_id(statement)
        self.write_attempts(self.attempt("Hessian matrix", targets=[ident]))
        self.write_mistakes([
            {
                "date": "2026-10-30",
                "concept": "Hessian matrix",
                "error_type": "application",
                "self_attribution": f"[targets: {ident}] treated PSD as sufficient",
            }
        ])
        before = self.state_bytes()
        node_mastery.build(self.root, TODAY)
        node_mastery.audit(self.root, TODAY)
        self.assertEqual(before, self.state_bytes())

    # -- strict links ------------------------------------------------------
    def test_target_links_attach_attempts_and_mistakes(self) -> None:
        statement = "The Hessian is symmetric when second partials are continuous."
        self.seed({"name": "Hessian symmetry", "statement": statement})
        ident = graph.node_id(statement)
        self.write_attempts(self.attempt("Hessian matrix", targets=[ident]))
        self.write_mistakes([
            {
                "date": "2026-10-30",
                "concept": "Hessian matrix",
                "error_type": "application",
                "self_attribution": f"[miss: discrimination] [targets: {ident}] treated PSD as sufficient",
            }
        ])

        record = node_mastery.build(self.root, TODAY)["nodes"][ident]
        self.assertEqual(record["strict"]["fails"], 1)
        self.assertEqual(record["strict"]["links"]["by_target"], 1)
        self.assertEqual(record["strict"]["last_fail"], "2026-10-30")
        self.assertEqual(record["strict"]["mistake_tiers"]["active"], 1)
        mistake = record["strict"]["mistakes"][0]
        self.assertEqual(mistake["link"], "target")
        self.assertEqual(mistake["miss_class"], "discrimination")
        self.assertIn("treated PSD as sufficient", mistake["self_attribution"])

    def test_unique_alias_links_attempts_and_mistakes_by_concept(self) -> None:
        self.seed({
            "name": "Hessian symmetry",
            "statement": "The Hessian is symmetric when second partials are continuous.",
            "aliases": ["Hessian matrix"],
        })
        ident = graph.node_id("The Hessian is symmetric when second partials are continuous.")
        self.write_attempts(self.attempt("Hessian  Matrix"))
        self.write_mistakes([
            {
                "date": "2026-10-30",
                "concept": "Hessian Matrix",
                "error_type": "structural",
                "self_attribution": "confused symmetry with definiteness",
            }
        ])

        record = node_mastery.build(self.root, TODAY)["nodes"][ident]
        self.assertEqual(record["strict"]["links"]["by_concept"], 1)
        self.assertEqual(record["strict"]["mistakes"][0]["link"], "concept")

    def test_ambiguous_concept_is_reported_not_attributed(self) -> None:
        self.seed(
            {
                "name": "Hessian matrix",
                "statement": "The Hessian is the matrix of second partials.",
            },
            {
                "name": "Hessian definiteness",
                "statement": "Hessian definiteness classifies critical points.",
                "aliases": ["Hessian matrix"],
            },
        )
        self.write_attempts(self.attempt("Hessian matrix"))

        view = node_mastery.build(self.root, TODAY)
        self.assertEqual(len(view["ambiguous"]["Hessian matrix"]), 2)
        for record in view["nodes"].values():
            self.assertEqual(record["strict"]["attempts"], [])

        self.write_mistakes([
            {
                "date": "2026-10-30",
                "concept": "Hessian matrix",
                "error_type": "application",
                "self_attribution": "could be either proposition",
            }
        ])
        view = node_mastery.build(self.root, TODAY)
        for record in view["nodes"].values():
            self.assertEqual(record["strict"]["mistakes"], [])

        result = node_mastery.audit(self.root, TODAY)
        self.assertEqual(result["links"]["ambiguous_concepts"], 1)
        self.assertEqual(result["coverage"]["nodes_with_evidence"], 0)

    def test_pipes_inside_table_cells_are_tolerated(self) -> None:
        self.seed({
            "name": "Hessian matrix",
            "statement": "The Hessian is the matrix of second partials.",
        })
        ident = graph.node_id("The Hessian is the matrix of second partials.")
        (self.core / "🧯 Mistakes.md").write_text(
            "| Date | Concept | Question | Expected | Error Type | Self-Attribution | Status | Retries | Next Retry |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| 2026-10-30 | Hessian matrix | q | expected a | expected b | application "
            "| [miss: cue] why | more detail | active | 0 | 2026-12-01 |\n",
            encoding="utf-8",
        )
        record = node_mastery.build(self.root, TODAY)["nodes"][ident]
        self.assertEqual(len(record["strict"]["mistakes"]), 1)
        mistake = record["strict"]["mistakes"][0]
        self.assertEqual(mistake["miss_class"], "cue")
        self.assertEqual(mistake["self_attribution"], "why | more detail")

    def test_chain_target_attaches_to_chain_and_conclusion(self) -> None:
        receipt = self.merge({
            "nodes": [
                {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                {"name": "E", "statement": "E is true.", "provenance": [prov()]},
            ],
            "chains": [{"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]}],
        })
        chain = receipt["created_chains"][0]
        conclusion = graph.node_id("E is true.")
        self.write_attempts(self.attempt("E", targets=[chain]))

        view = node_mastery.build(self.root, TODAY)
        self.assertEqual(len(view["chains"][chain]["strict"]["attempts"]), 1)
        self.assertEqual(view["chains"][chain]["strict"]["fails"], 1)
        self.assertEqual(view["nodes"][conclusion]["strict"]["links"]["by_chain"], 1)
        self.assertEqual(view["nodes"][conclusion]["strict"]["attempts"][0]["link"], "chain")

    def test_string_and_mixed_targets_are_classified(self) -> None:
        self.seed({"name": "A", "statement": "A is true."})
        ident = graph.node_id("A is true.")
        self.write_attempts(self.attempt("A", targets=f"{ident}, n_zzzzzz"))
        view = node_mastery.build(self.root, TODAY)
        self.assertEqual(view["nodes"][ident]["strict"]["links"]["by_target"], 1)
        self.assertIn("n_zzzzzz", view["stale_targets"])

    def test_prefixes_strip_in_any_order(self) -> None:
        prereq, miss_class, targets, text = node_mastery._strip_prefixes(
            "[targets: n_aaaaaa] [miss: execution] [prereq: Linear Algebra] why"
        )
        self.assertEqual(prereq, "Linear Algebra")
        self.assertEqual(miss_class, "execution")
        self.assertEqual(targets, ["n_aaaaaa"])
        self.assertEqual(text, "why")

    # -- history tiers -----------------------------------------------------
    def test_graduated_mistakes_are_kept_with_decay(self) -> None:
        self.seed({
            "name": "Hessian matrix",
            "statement": "The Hessian is the matrix of second partials.",
        })
        ident = graph.node_id("The Hessian is the matrix of second partials.")
        self.write_mistakes([
            {
                "date": "2026-10-01",
                "concept": "Hessian matrix",
                "error_type": "application",
                "self_attribution": "open slip",
                "status": "active",
            },
            {
                "date": "2026-11-04",
                "concept": "Hessian matrix",
                "error_type": "structural",
                "self_attribution": "repaired, but keep the transfer test",
                "status": "graduated",
            },
        ])

        record = node_mastery.build(self.root, TODAY)["nodes"][ident]
        self.assertEqual(len(record["strict"]["mistakes"]), 2)
        self.assertEqual(record["strict"]["mistake_tiers"], {"active": 1, "review": 0, "graduated": 1})
        by_status = {row["status"]: row for row in record["strict"]["mistakes"]}
        self.assertEqual(by_status["active"]["weight"], 1.0)
        self.assertLess(by_status["graduated"]["weight"], 1.0)
        self.assertGreater(by_status["graduated"]["weight"], 0.0)

    def test_history_tiers_are_counted(self) -> None:
        self.seed({
            "name": "Hessian matrix",
            "statement": "The Hessian is the matrix of second partials.",
        })
        self.write_mistakes([
            {"date": "2026-09-01", "concept": "Hessian matrix", "error_type": "structural", "status": "active"},
            {"date": "2026-09-02", "concept": "Hessian matrix", "error_type": "structural", "status": "review"},
            {"date": "2026-09-03", "concept": "Hessian matrix", "error_type": "structural", "status": "graduated"},
        ])
        result = node_mastery.audit(self.root, TODAY)
        self.assertEqual(result["mistakes"]["tiers"], {"active": 1, "review": 1, "graduated": 1})

    # -- reporting ---------------------------------------------------------
    def test_stale_targets_are_reported_not_resolved(self) -> None:
        self.seed({
            "name": "Hessian matrix",
            "statement": "The Hessian is the matrix of second partials.",
        })
        self.write_attempts(self.attempt("Hessian matrix", targets=["n_aaaaaa"]))
        view = node_mastery.build(self.root, TODAY)
        self.assertEqual(view["stale_targets"], ["n_aaaaaa"])
        self.assertEqual(list(view["nodes"].values())[0]["strict"]["attempts"], [])
        self.assertEqual(node_mastery.audit(self.root, TODAY)["links"]["stale_targets"], 1)

    def test_audit_reports_coverage(self) -> None:
        self.seed(
            {"name": "A", "statement": "A is true."},
            {"name": "B", "statement": "B is true."},
        )
        ident = graph.node_id("A is true.")
        self.write_attempts(self.attempt("A", targets=[ident]))
        coverage = node_mastery.audit(self.root, TODAY)["coverage"]
        self.assertEqual(coverage["nodes_with_evidence"], 1)
        self.assertEqual(coverage["nodes_total"], 2)
        self.assertEqual(coverage["pct"], 50.0)

    def test_report_is_deterministic(self) -> None:
        self.seed({"name": "A", "statement": "A is true."})
        ident = graph.node_id("A is true.")
        self.write_attempts(self.attempt("A", targets=[ident]))
        first = json.dumps(node_mastery.build(self.root, TODAY), sort_keys=True)
        second = json.dumps(node_mastery.build(self.root, TODAY), sort_keys=True)
        self.assertEqual(first, second)

    # -- budgeted context --------------------------------------------------
    def test_context_index_is_complete_and_detail_fits_budget(self) -> None:
        self.seed(
            {"name": "Hessian symmetry", "statement": "Hessian symmetry follows from Clairaut.", "aliases": ["Hessian matrix"]},
            {"name": "Hessian definiteness", "statement": "Hessian definiteness classifies critical points.", "aliases": ["Hessian matrix"]},
            {"name": "Hessian eigenvalues", "statement": "Hessian eigenvalues give curvature directions.", "aliases": ["Hessian matrix"]},
            {"name": "Jacobian rows", "statement": "The Jacobian stacks first partials."},
        )
        ident = graph.node_id("Hessian symmetry follows from Clairaut.")
        self.write_attempts(self.attempt("Hessian matrix", targets=[ident]))
        block = node_mastery.build_context(
            self.root, ["Hessian matrix"], today=TODAY, max_bytes=8000
        )
        self.assertLessEqual(block["budget"]["body_bytes"], 8000)
        index_ids = {entry["id"] for entry in block["index"]}
        self.assertEqual(len(index_ids), 3)  # Jacobian is not a Hessian match
        self.assertIn(ident, index_ids)
        # The target-linked node outranks the concept-only matches.
        self.assertEqual(block["propositions"][0]["id"], ident)
        self.assertEqual(block["omitted"]["reason"], "")
        self.assertTrue(node_mastery.verify_block(self._write_block(block))["ok"])

    def test_context_respects_a_small_budget_and_shows_omissions(self) -> None:
        for number in range(20):
            self.seed({
                "name": f"Hessian claim {number}",
                "statement": f"Hessian statement {number}: " + ("curvature " * 120),
            })
        block = node_mastery.build_context(
            self.root, ["Hessian"], today=TODAY, max_bytes=2000
        )
        self.assertLessEqual(block["budget"]["body_bytes"], 2000)
        self.assertGreater(block["omitted"]["propositions"], 0)
        self.assertEqual(block["omitted"]["reason"], "budget")
        self.assertTrue(block["omitted"]["next_best"])
        self.assertTrue(node_mastery.verify_block(self._write_block(block))["ok"])

    def test_context_keeps_graduated_mistakes_with_decay(self) -> None:
        self.seed({
            "name": "Hessian matrix",
            "statement": "The Hessian is the matrix of second partials.",
        })
        self.write_mistakes([
            {
                "date": "2026-11-04",
                "concept": "Hessian matrix",
                "error_type": "structural",
                "self_attribution": "repaired, keep testing transfer",
                "status": "graduated",
            }
        ])
        block = node_mastery.build_context(
            self.root, ["Hessian matrix"], today=TODAY, max_bytes=8000
        )
        mistake = block["propositions"][0]["mistakes"][0]
        self.assertEqual(mistake["status"], "graduated")
        self.assertLess(mistake["weight"], 1.0)
        self.assertEqual(block["mistakes"][0]["node"], block["propositions"][0]["id"])

    def test_context_chains_join_only_when_every_endpoint_is_in_detail(self) -> None:
        receipt = self.merge({
            "nodes": [
                {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                {"name": "B", "statement": "B is true.", "provenance": [prov()]},
            ],
            "chains": [{"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]}],
        })
        block = node_mastery.build_context(
            self.root, ["A", "B"], today=TODAY, max_bytes=8000
        )
        self.assertEqual([chain["id"] for chain in block["chains"]], [receipt["created_chains"][0]])
        self.assertEqual(block["budget"]["body_bytes"], node_mastery._json_bytes(
            {key: value for key, value in block.items() if key != "budget"}
        ))

    def test_verify_rejects_broken_index_or_budget_math(self) -> None:
        self.seed({"name": "Hessian matrix", "statement": "The Hessian is symmetric."})
        block = node_mastery.build_context(
            self.root, ["Hessian matrix"], today=TODAY, max_bytes=8000
        )
        path = self._write_block(block)
        self.assertTrue(node_mastery.verify_block(path)["ok"])

        tampered = json.loads(path.read_text())
        tampered["index"] = []
        path.write_text(json.dumps(tampered))
        self.assertFalse(node_mastery.verify_block(path)["ok"])

        tampered = json.loads(json.dumps(block))
        tampered["budget"]["body_bytes"] = 1
        path.write_text(json.dumps(tampered))
        self.assertFalse(node_mastery.verify_block(path)["ok"])

    def test_context_cli_writes_a_block_and_verify_receipts(self) -> None:
        self.seed({"name": "Hessian matrix", "statement": "The Hessian is symmetric."})
        out = self.root / ".tmp" / "prior.json"
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = node_mastery.main([
                "--root", str(self.root), "context", "--concepts", "Hessian matrix",
                "--out", str(out), "--today", "2026-11-05",
            ])
        self.assertEqual(code, 0)
        self.assertIn("PRIOR_CONTEXT:", buffer.getvalue())
        self.assertTrue(out.is_file())

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = node_mastery.main(["--root", str(self.root), "verify", "--file", str(out)])
        self.assertEqual(code, 0)
        self.assertIn("PRIOR_BUDGET_OK:", buffer.getvalue())

    def _write_block(self, block: dict) -> Path:
        path = self.root / ".tmp" / "prior.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(block), encoding="utf-8")
        return path

    def test_cli_audit_emits_json(self) -> None:
        self.seed({"name": "A", "statement": "A is true."})
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = node_mastery.main(
                ["--root", str(self.root), "audit", "--json", "--today", "2026-11-05"]
            )
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertEqual(parsed["coverage"]["nodes_total"], 1)


if __name__ == "__main__":
    unittest.main()
