#!/usr/bin/env python3
"""Behavior tests for pi/graph.py — the propositions + reasoning-chains ledger.

These tests run without the learning system (temp roots only), so they are part
of the offline `learn-check` corpus and the contract-coverage binding.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYER = HERE.parent.parent

_SPEC = importlib.util.spec_from_file_location("learning_graph", LAYER / "pi" / "graph.py")
assert _SPEC and _SPEC.loader
graph = importlib.util.module_from_spec(_SPEC)
sys.modules["learning_graph"] = graph
_SPEC.loader.exec_module(graph)


def prov(path: str = "Learning System/Lessons/lesson.md", **extra) -> dict:
    return {"file": path, **extra}


class GraphCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "Learning System" / "Core").mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- helpers -----------------------------------------------------------
    def merge(self, spec: dict) -> dict:
        current = graph.load(self.root)
        plan = graph.plan_merge(current, spec)
        return graph.apply_merge(self.root, plan)

    def view(self) -> dict:
        return graph.derived(self.root)

    def nodes_file(self) -> Path:
        return self.root / graph.GRAPH_DIR / graph.NODES_FILE

    def chains_file(self) -> Path:
        return self.root / graph.GRAPH_DIR / graph.CHAINS_FILE

    def cli(self, *args: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = graph.main(["--root", str(self.root), *args])
        return code, buffer.getvalue()

    # -- propositions ------------------------------------------------------
    def test_merge_creates_propositions_with_deterministic_ids(self) -> None:
        spec = {
            "nodes": [
                {"name": "Row independence", "statement": "A linear layer acts on each row independently.", "provenance": [prov()]},
                {"name": "Softmax rows", "statement": "Softmax normalizes each row of the score matrix.", "provenance": [prov()]},
            ]
        }
        receipt = self.merge(spec)
        self.assertEqual(receipt["nodes_created"], 2)
        self.assertEqual(receipt["nodes_linked"], 0)
        loaded = graph.load(self.root)
        expected = graph.node_id("A linear layer acts on each row independently.")
        self.assertIn(expected, loaded["nodes"])
        self.assertEqual(set(receipt["created_nodes"]), set(loaded["nodes"]))

    def test_merge_is_idempotent_for_the_same_statement(self) -> None:
        spec = {
            "nodes": [
                {"name": "Row independence", "statement": "A linear layer acts on each row independently.", "provenance": [prov()]},
            ]
        }
        first = self.merge(spec)
        second = self.merge(spec)
        self.assertEqual(first["nodes_created"], 1)
        self.assertEqual(second["nodes_created"], 0)
        self.assertEqual(second["nodes_linked"], 1)
        loaded = graph.load(self.root)
        self.assertEqual(len(loaded["nodes"]), 1)
        # The define line and the link line both stay on disk (append-only).
        self.assertEqual(len(self.nodes_file().read_text().strip().splitlines()), 3)

    def test_link_appends_alias_and_provenance_without_overwriting(self) -> None:
        node_id = self.merge(
            {"nodes": [{"name": "Row independence", "statement": "A linear layer acts on each row independently.", "provenance": [prov()]}]}
        )["created_nodes"][0]
        self.merge(
            {
                "nodes": [
                    {
                        "link_to": node_id,
                        "statement": "Rows of X do not influence each other under W.",
                        "provenance": [prov("Learning System/Sessions/session.md")],
                    }
                ]
            }
        )
        node = graph.load(self.root)["nodes"][node_id]
        self.assertEqual(node["statement"], "A linear layer acts on each row independently.")
        self.assertIn("Rows of X do not influence each other under W.", node["aliases"])
        self.assertEqual(len(node["provenance"]), 2)

    def test_node_requires_statement_and_provenance(self) -> None:
        with self.assertRaises(graph.GraphError):
            graph.plan_merge(graph.load(self.root), {"nodes": [{"name": "No statement"}]})
        with self.assertRaises(graph.GraphError):
            graph.plan_merge(
                graph.load(self.root),
                {"nodes": [{"name": "No provenance", "statement": "Something true."}]},
            )

    def test_learner_state_field_is_rejected(self) -> None:
        spec = {
            "nodes": [
                {
                    "name": "Row independence",
                    "statement": "A linear layer acts on each row independently.",
                    "provenance": [prov()],
                    "mastery": 2,
                }
            ]
        }
        with self.assertRaises(graph.GraphError) as caught:
            graph.plan_merge(graph.load(self.root), spec)
        self.assertIn("learner state", str(caught.exception))

    def test_rejected_merge_writes_nothing(self) -> None:
        spec = '{"nodes": [{"name": "x", "statement": "y", "provenance": [{"mastery": 1}]}]}'
        code = graph.cmd_merge(self.root, io.StringIO(spec))
        self.assertEqual(code, 1)
        self.assertFalse((self.root / graph.GRAPH_DIR).exists())

    # -- chains ------------------------------------------------------------
    def test_chain_with_spec_index_refs(self) -> None:
        spec = {
            "nodes": [
                {"name": "A", "statement": "Premise A is true.", "provenance": [prov()]},
                {"name": "B", "statement": "Premise B is true.", "provenance": [prov()]},
                {"name": "C", "statement": "Conclusion C follows.", "provenance": [prov()]},
            ],
            "chains": [
                {"premises": ["@0", "@1"], "conclusion": "@2", "statement": "A ∧ B ⟹ C", "provenance": [prov()]}
            ],
        }
        receipt = self.merge(spec)
        self.assertEqual(receipt["chains_created"], 1)
        chain = graph.load(self.root)["chains"][receipt["created_chains"][0]]
        node_ids = {
            graph.node_id("Premise A is true."),
            graph.node_id("Premise B is true."),
        }
        self.assertEqual(set(chain["premises"]), node_ids)

    def test_chain_is_deduped_by_premise_set(self) -> None:
        base = {
            "nodes": [
                {"name": "A", "statement": "Premise A.", "provenance": [prov()]},
                {"name": "B", "statement": "Premise B.", "provenance": [prov()]},
                {"name": "C", "statement": "Conclusion C.", "provenance": [prov()]},
            ]
        }
        self.merge({**base, "chains": [{"premises": ["@0", "@1"], "conclusion": "@2", "provenance": [prov()]}]})
        second = self.merge(
            {**base, "chains": [{"premises": ["@1", "@0"], "conclusion": "@2", "provenance": [prov("Learning System/Sessions/s2.md")]}]}
        )
        self.assertEqual(second["chains_created"], 0)
        self.assertEqual(second["chains_linked"], 1)
        self.assertEqual(len(graph.load(self.root)["chains"]), 1)

    def test_chain_requires_resolvable_references(self) -> None:
        with self.assertRaises(graph.GraphError) as caught:
            graph.plan_merge(
                graph.load(self.root),
                {"chains": [{"premises": ["n_deadbeef00"], "conclusion": "n_feedface00", "provenance": [prov()]}]},
            )
        self.assertIn("unknown premise", str(caught.exception).lower())

    def test_chain_rejects_conclusion_as_premise(self) -> None:
        spec = {
            "nodes": [
                {"name": "A", "statement": "Only premise A.", "provenance": [prov()]},
            ],
            "chains": [{"premises": ["@0"], "conclusion": "@0", "provenance": [prov()]}],
        }
        with self.assertRaises(graph.GraphError):
            graph.plan_merge(graph.load(self.root), spec)

    # -- derived view ------------------------------------------------------
    def test_export_derives_one_implication_node_per_argument(self) -> None:
        spec = {
            "nodes": [
                {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                {"name": "B", "statement": "B is true.", "provenance": [prov()]},
                {"name": "C", "statement": "C is true.", "provenance": [prov()]},
                {"name": "D", "statement": "D is true.", "provenance": [prov()]},
                {"name": "E", "statement": "E is true.", "provenance": [prov()]},
            ],
            "chains": [
                {"premises": ["@0", "@1"], "conclusion": "@4", "provenance": [prov()]},
                {"premises": ["@2", "@3"], "conclusion": "@4", "provenance": [prov()]},
            ],
        }
        self.merge(spec)
        view = self.view()
        implications = [n for n in view["nodes"] if n["kind"] == "implication"]
        self.assertEqual(len(implications), 2)
        self.assertEqual(len(view["edges"]), 6)
        # Two independent arguments for E stay two diamonds: no stored edge list.
        self.assertNotIn('"edges"', self.nodes_file().read_text())
        self.assertNotIn('"edges"', self.chains_file().read_text())

    def test_export_mermaid_renders_implications(self) -> None:
        self.merge(
            {
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [{"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]}],
            }
        )
        code, out = self.cli("export")
        self.assertEqual(code, 0)
        self.assertIn("graph TD", out)
        self.assertIn('{{"⟹"}}', out)

    def test_retract_hides_node_and_drops_dependent_chains(self) -> None:
        receipt = self.merge(
            {
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "B", "statement": "B is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [{"premises": ["@0", "@1"], "conclusion": "@2", "provenance": [prov()]}],
            }
        )
        conclusion = graph.node_id("E is true.")
        self.assertEqual(graph.cmd_retract(self.root, conclusion, "wrong claim"), 0)
        view = self.view()
        self.assertNotIn(conclusion, {n["id"] for n in view["nodes"] if n["kind"] == "proposition"})
        self.assertEqual(view["dropped_chains"], 1)
        self.assertEqual(view["dangling_chains"], 0)
        self.assertEqual(
            [n for n in view["nodes"] if n["kind"] == "implication"], []
        )
        self.assertTrue(receipt["created_chains"])

    def test_chain_retract_removes_the_argument(self) -> None:
        receipt = self.merge(
            {
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [{"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]}],
            }
        )
        chain_id = receipt["created_chains"][0]
        self.assertEqual(graph.cmd_retract(self.root, chain_id, "bad entailment"), 0)
        view = self.view()
        self.assertEqual([n for n in view["nodes"] if n["kind"] == "implication"], [])

    def test_dangling_chain_is_an_integrity_error(self) -> None:
        self.merge(
            {"nodes": [{"name": "A", "statement": "A is true.", "provenance": [prov()]}]}
        )
        gdir = self.root / graph.GRAPH_DIR
        gdir.mkdir(parents=True, exist_ok=True)
        with (gdir / graph.CHAINS_FILE).open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "id": "arg_deadbeef00",
                        "premises": [graph.node_id("A is true.")],
                        "conclusion": "n_missing0000",
                        "provenance": [prov()],
                    }
                )
                + "\n"
            )
        code, _ = self.cli("status", "--json")
        self.assertEqual(code, 1)

    def test_status_reports_malformed_line(self) -> None:
        gdir = self.root / graph.GRAPH_DIR
        gdir.mkdir(parents=True, exist_ok=True)
        (gdir / graph.NODES_FILE).write_text("this is not json\n", encoding="utf-8")
        code, out = self.cli("status")
        self.assertEqual(code, 1)
        self.assertIn("malformed JSON", out)

    def test_list_filters_by_session(self) -> None:
        self.merge(
            {
                "session": "ses_one",
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [{"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]}],
            }
        )
        self.merge(
            {
                "session": "ses_two",
                "nodes": [{"name": "B", "statement": "B is true.", "provenance": [prov()]}],
            }
        )
        code, out = self.cli("list", "--json", "--session", "ses_one")
        self.assertEqual(code, 0)
        listed = json.loads(out)
        self.assertEqual([n["name"] for n in listed["nodes"]], ["A", "E"])
        self.assertEqual(len(listed["chains"]), 1)
        self.assertEqual(listed["chains"][0]["conclusion"], graph.node_id("E is true."))

    # -- fix loop and spec hygiene ----------------------------------------
    def test_retracted_node_is_revived_by_remerge(self) -> None:
        node_id = self.merge(
            {"nodes": [{"name": "A", "statement": "A is true.", "provenance": [prov()]}]}
        )["created_nodes"][0]
        self.assertEqual(graph.cmd_retract(self.root, node_id, "mistake"), 0)
        self.assertIn(node_id, graph.load(self.root)["retracted_nodes"])
        receipt = self.merge(
            {
                "nodes": [
                    {
                        "name": "A",
                        "statement": "A is true.",
                        "provenance": [prov("Learning System/Sessions/s2.md")],
                    }
                ]
            }
        )
        self.assertEqual(receipt["nodes_created"], 1)
        loaded = graph.load(self.root)
        self.assertNotIn(node_id, loaded["retracted_nodes"])
        self.assertIn(node_id, loaded["nodes"])
        self.assertEqual(len(loaded["nodes"][node_id]["provenance"]), 2)
        self.assertEqual(loaded["problems"], [])

    def test_retracted_chain_is_revived_by_reassert(self) -> None:
        receipt = self.merge(
            {
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [{"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]}],
            }
        )
        chain_id = receipt["created_chains"][0]
        self.assertEqual(graph.cmd_retract(self.root, chain_id, "bad entailment"), 0)
        again = self.merge(
            {
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [
                    {
                        "premises": ["@0"],
                        "conclusion": "@1",
                        "provenance": [prov("Learning System/Sessions/s2.md")],
                    }
                ],
            }
        )
        self.assertEqual(again["chains_created"], 1)
        loaded = graph.load(self.root)
        self.assertNotIn(chain_id, loaded["retracted_chains"])
        self.assertEqual(len(loaded["chains"][chain_id]["provenance"]), 2)
        self.assertEqual(loaded["problems"], [])

    def test_duplicate_chains_in_one_spec_link(self) -> None:
        receipt = self.merge(
            {
                "nodes": [
                    {"name": "A", "statement": "A is true.", "provenance": [prov()]},
                    {"name": "E", "statement": "E is true.", "provenance": [prov()]},
                ],
                "chains": [
                    {"premises": ["@0"], "conclusion": "@1", "provenance": [prov()]},
                    {"premises": ["@0"], "conclusion": "@1", "provenance": [prov("Learning System/Sessions/s2.md")]},
                ],
            }
        )
        self.assertEqual(receipt["chains_created"], 1)
        self.assertEqual(receipt["chains_linked"], 1)
        self.assertEqual(len(set(receipt["created_chains"] + receipt["linked_chains"])), 1)
        loaded = graph.load(self.root)
        self.assertEqual(len(loaded["chains"]), 1)
        self.assertEqual(loaded["problems"], [])

    def test_negative_spec_index_is_rejected(self) -> None:
        spec = {
            "nodes": [{"name": "A", "statement": "A is true.", "provenance": [prov()]}],
            "chains": [{"premises": ["@0"], "conclusion": "@-1", "provenance": [prov()]}],
        }
        with self.assertRaises(graph.GraphError):
            graph.plan_merge(graph.load(self.root), spec)

    def test_session_only_provenance_is_rejected(self) -> None:
        spec = {
            "nodes": [
                {"name": "A", "statement": "A is true.", "provenance": [{"session": "ses_one"}]}
            ]
        }
        with self.assertRaises(graph.GraphError) as caught:
            graph.plan_merge(graph.load(self.root), spec)
        self.assertIn("non-empty `file`", str(caught.exception))

    def test_top_level_notes_are_accepted_and_ignored(self) -> None:
        receipt = self.merge(
            {
                "nodes": [{"name": "A", "statement": "A is true.", "provenance": [prov()]}],
                "chains": [],
                "notes": ["material gap: the source skipped the proof"],
            }
        )
        self.assertEqual(receipt["nodes_created"], 1)
        self.assertEqual(graph.load(self.root)["problems"], [])


if __name__ == "__main__":
    unittest.main()
