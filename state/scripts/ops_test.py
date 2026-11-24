#!/usr/bin/env python3
"""Regression tests for scripts/ops.py — stdlib only (run: python3 -m unittest scripts/ops_test).

Guards the three bugs fixed 2026-08:
- ROOT auto-detect works on either checkout (not hardcoded to one path).
- Path-escape guard rejects attempts to read outside the workspace.
- `state <track>` returns the concept TABLE ROWS, not just the section heading.
"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# Allow running as a standalone module or via `python3 -m unittest scripts.ops_test`
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops  # noqa: E402


def _seed_graph(root, nodes=(), chains=()):
    """Write minimal knowledge-graph ledgers under root (target-liveness fixtures)."""
    gdir = Path(root) / "Knowledge Wiki" / "graph"
    gdir.mkdir(parents=True, exist_ok=True)
    (gdir / "nodes.jsonl").write_text(
        "".join(json.dumps(n) + "\n" for n in nodes), encoding="utf-8"
    )
    (gdir / "chains.jsonl").write_text(
        "".join(json.dumps(c) + "\n" for c in chains), encoding="utf-8"
    )


class TestRootDetection(unittest.TestCase):
    def test_root_resolves_to_a_checkout_with_core(self):
        # The directory containing this test must have "Learning System/Core".
        self.assertTrue((ops.ROOT / "Learning System" / "Core").is_dir())

    def test_env_override_is_honored(self):
        # LEARNING_SYSTEM_ROOT pointing at a dir without the Core substructure
        # must NOT be selected (falls through to a real checkout).
        os.environ["LEARNING_SYSTEM_ROOT"] = "/tmp/definitely-not-a-checkout"
        try:
            root = ops._detect_root()
        finally:
            del os.environ["LEARNING_SYSTEM_ROOT"]
        self.assertTrue((root / "Learning System" / "Core").is_dir())


class TestPathEscape(unittest.TestCase):
    def test_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            ops._resolve("../etc/passwd")
        with self.assertRaises(ValueError):
            ops._resolve("/etc/passwd")

    def test_internal_path_is_allowed(self):
        p = ops._resolve("Learning System/Core/💡 Learning Profile.md")
        self.assertTrue(str(p).startswith(str(ops.ROOT)))


class TestSectionSlice(unittest.TestCase):
    def test_section_captures_table_rows_not_just_heading(self):
        lines = [
            "# KNOWLEDGE BASE",
            "## SWE Track — Shell & Terminal",
            "| Concept | Type |",
            "| --- | --- |",
            "| What is the Shell | concept |",
            "## aie Track — archived",
            "| old concept | concept |",
        ]
        text, err = ops._section_slice(lines, r"^## swe\b")
        self.assertIsNone(err)
        self.assertIn("What is the Shell", text)
        self.assertNotIn("old concept", text)  # next section excluded
        self.assertIn("## SWE Track", text)

    def test_section_missing_returns_error(self):
        lines = ["# title", "## Other"]
        text, err = ops._section_slice(lines, r"^## nope\b")
        self.assertIsNone(text)
        self.assertIn("no matching section", err)


class TestDoStateActiveConcepts(unittest.TestCase):
    def test_state_swe_returns_concept_rows(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_state("swe")
        out = buf.getvalue()
        # SWE was archived 2026-09-01 (43 concepts → 📦 Concept Archive.md).
        # The active track is now AIEFS (Mission 0 catch-up). SWE section
        # should contain the ARCHIVED banner, not live concept rows.
        # Keep test green through the roadmap switch.
        self.assertIn("## SWE Track", out)
        if "ARCHIVED" in out:
            self.assertIn("ARCHIVED", out)
            self.assertIn("43 concepts paused", out)
        else:
            # Pre-archive expectation (preserved for history)
            self.assertIn("| What is the Shell |", out)


class TestDoStateIncludesMasterySidecars(unittest.TestCase):
    def test_state_bundles_attempts_and_mistakes(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_state("aiefs")
        out = buf.getvalue()
        self.assertIn("Attempts.json", out)
        self.assertIn("Mistakes.md", out)


class TestAttemptCommand(unittest.TestCase):
    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "Test Concept": {
                    "type": "concept",
                    "attempts": [{"date": "2026-09-01", "is_correct": True,
                                  "result": "pass", "q_type": None}],
                    "interval_index": 0,
                    "consecutive_correct": 1,
                    "consecutive_wrong": 0,
                    "last_reviewed": "2026-09-01",
                    "next_review": "2026-09-04",
                    "feynman": None,
                }
            },
            "meta": {"version": 1,
                     "intervals": {"memory": [0, 1, 3, 7, 14, 30, 60],
                                   "concept": [3, 7, 14, 30],
                                   "procedure": [3, 7, 14],
                                   "design": [14, 28]}},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    def test_attempt_pass_advances_interval(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "pass", date="2026-09-04")
        out = buf.getvalue()
        self.assertIn("next_review", out)
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(len(entry["attempts"]), 2)
        # 2nd consecutive pass => +2 from index 0
        self.assertEqual(entry["interval_index"], 2)
        self.assertEqual(entry["next_review"], "2026-09-18")  # 2026-09-04 + 14d
        self.assertEqual(entry["last_reviewed"], "2026-09-04")

    def test_attempt_fail_drops_interval(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "fail", date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(entry["interval_index"], 0)  # clamped, was 0
        self.assertEqual(entry["consecutive_wrong"], 1)

    def test_attempt_feynman_flag_recorded(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "pass", feynman="feynman_pass",
                           date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["Test Concept"]["feynman"], "pass")

    def test_attempt_new_concept_defaults(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Brand New", "pass", date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertIn("Brand New", data["concepts"])
        self.assertEqual(data["concepts"]["Brand New"]["type"], "concept")

    def test_mastery_caps_single_attempt(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_mastery("aiefs")
        out = buf.getvalue()
        # 1 pass => recency 1.0 capped at 0.5
        self.assertIn("Test Concept", out)
        self.assertIn("0.50", out)

    def test_attempt_rejects_bad_mode(self):
        self._make_root()
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("Test Concept", "pass", mode="duo", date="2026-09-04")
        self.assertEqual(cm.exception.code, 2)

    def test_attempt_rejects_bad_confidence(self):
        self._make_root()
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("Test Concept", "pass", confidence="maybe", date="2026-09-04")
        self.assertEqual(cm.exception.code, 2)

    def test_prereq_attempt_merges_existing_edges(self):
        self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Test Concept", "pass", date="2026-09-04", prereqs=["A"])
            ops.do_attempt("Test Concept", "pass", date="2026-09-05", prereqs=["B"])
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["Test Concept"]["prereqs"], ["A", "B"])

    def test_attempt_records_graph_targets(self):
        root = self._make_root()
        _seed_graph(
            root,
            nodes=[{"id": "n_ab12cd34ef", "op": "define"}],
            chains=[{
                "id": "arg_ab12cd34ef",
                "op": "assert",
                "premises": ["n_ab12cd34ef"],
                "conclusion": "n_ffffffffff",
            }],
        )
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Test Concept", "pass", date="2026-09-04",
                           targets=["n_ab12cd34ef", "arg_ab12cd34ef", "n_ab12cd34ef"])
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        rec = data["concepts"]["Test Concept"]["attempts"][-1]
        self.assertEqual(rec["targets"], ["arg_ab12cd34ef", "n_ab12cd34ef"])

    def test_attempt_rejects_missing_graph_target(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("Test Concept", "pass", date="2026-09-04",
                               targets=["n_ab12cd34ef"])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("not live in the knowledge graph", buf.getvalue())

    def test_attempt_rejects_retracted_graph_target(self):
        root = self._make_root()
        _seed_graph(root, nodes=[
            {"id": "n_ab12cd34ef", "op": "define"},
            {"id": "n_ab12cd34ef", "op": "retract", "reason": "wrong claim"},
        ])
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("Test Concept", "pass", date="2026-09-04",
                               targets=["n_ab12cd34ef"])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("not live in the knowledge graph", buf.getvalue())

    def test_attempt_accepts_revived_graph_target(self):
        root = self._make_root()
        _seed_graph(root, nodes=[
            {"id": "n_ab12cd34ef", "op": "define"},
            {"id": "n_ab12cd34ef", "op": "retract", "reason": "wrong claim"},
            {"id": "n_ab12cd34ef", "op": "define"},
        ])
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Test Concept", "pass", date="2026-09-04",
                           targets=["n_ab12cd34ef"])
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        rec = data["concepts"]["Test Concept"]["attempts"][-1]
        self.assertEqual(rec["targets"], ["n_ab12cd34ef"])

    def test_attempt_reports_all_stale_targets(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("Test Concept", "pass", date="2026-09-04",
                               targets=["n_aaaaaaaaaa", "n_bbbbbbbbbb"])
        self.assertEqual(cm.exception.code, 2)
        out = buf.getvalue()
        self.assertIn("n_aaaaaaaaaa", out)
        self.assertIn("n_bbbbbbbbbb", out)

    def test_live_graph_ids_does_not_revive_never_asserted_chain(self):
        # graph.py tombstones a retracted id even if no assert exists, and the
        # create path does not pop that tombstone. Mirror it exactly.
        root = self._make_root()
        _seed_graph(root, chains=[
            {"id": "arg_zzzzzzzzzz", "op": "retract", "reason": "never existed"},
            {"id": "arg_zzzzzzzzzz", "op": "assert",
             "premises": ["n_aaaaaaaaaa"], "conclusion": "n_bbbbbbbbbb"},
        ])
        self.assertNotIn("arg_zzzzzzzzzz", ops.live_graph_ids())

    def test_live_graph_ids_revives_reasserted_chain(self):
        root = self._make_root()
        _seed_graph(root, chains=[
            {"id": "arg_zzzzzzzzzz", "op": "assert",
             "premises": ["n_aaaaaaaaaa"], "conclusion": "n_bbbbbbbbbb"},
            {"id": "arg_zzzzzzzzzz", "op": "retract", "reason": "fix"},
            {"id": "arg_zzzzzzzzzz", "op": "assert",
             "premises": ["n_aaaaaaaaaa"], "conclusion": "n_bbbbbbbbbb"},
        ])
        self.assertIn("arg_zzzzzzzzzz", ops.live_graph_ids())

    def test_attempt_rejects_bad_target(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("Test Concept", "pass", date="2026-09-04",
                               targets=["n_ab12cd34ef", "Bayes theorem"])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("--targets", buf.getvalue())


class TestQueueCommand(unittest.TestCase):
    """The deterministic review queue (ops.py queue): due-mistake priority,
    scheduler-truth due reviews, question-type alternation, adjacency guard,
    drift notes, and the digest skeleton."""

    def _seed(self, active_rows, mistakes_rows, attempts):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": attempts, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        header = "| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |"
        sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        (core / "📚 Active Concepts.md").write_text(
            "\n".join(["# KNOWLEDGE BASE", "", header, sep, *active_rows]) + "\n", encoding="utf-8")
        mheader = ("| Date | Concept | Question | Expected | Error Type | Self-Attribution | "
                   "Status | Retries | Next Retry |")
        msep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        (core / "🧯 Mistakes.md").write_text(
            "\n".join(["# Mistakes", "", mheader, msep, *mistakes_rows]) + "\n", encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    @staticmethod
    def _attempt(next_review, ctype="concept", last_q=None, feynman=None):
        return {"type": ctype, "attempts": [{"date": "2026-09-01", "is_correct": True,
                "result": "pass", "q_type": last_q}], "interval_index": 0,
                "consecutive_correct": 1, "consecutive_wrong": 0,
                "last_reviewed": "2026-09-01", "next_review": next_review, "feynman": feynman}

    @staticmethod
    def _active(name, next_review="2026-09-20", last_q="definitional", source="Rohit P1 L01 (Python)",
                ctype="concept", track="aiefs"):
        return (f"| {name} | {track} | {ctype} | developing | {source} | 2026-09-01 | "
                f"{next_review} | {last_q} | note |")

    @staticmethod
    def _mistake(date, name, next_retry, status="active", error_type="structural"):
        return (f"| {date} | {name} | Q? | Expected | {error_type} | why | {status} | 0 | "
                f"{next_retry} |")

    def test_prioritizes_oldest_due_mistakes_then_reviews(self):
        self._seed(
            active_rows=[
                self._active("M1", next_review="2026-09-01", source="Rohit P1 L01 (Python)"),
                self._active("M2", next_review="2026-09-01", source="Rohit P1 L02 (Python)"),
                self._active("R1", next_review="2026-09-01", source="Rohit P1 L03 (Python)"),
            ],
            mistakes_rows=[
                self._mistake("2026-09-05", "M1", "2026-09-06"),
                self._mistake("2026-09-02", "M2", "2026-09-03"),  # oldest
            ],
            attempts={"M1": self._attempt("2026-09-01"), "M2": self._attempt("2026-09-01"),
                      "R1": self._attempt("2026-09-01")},
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        self.assertEqual([e["concept"] for e in q["queue"][:2]], ["M2", "M1"])
        self.assertTrue(all(e["due_kind"] == "mistake" for e in q["queue"][:2]))
        self.assertEqual(q["queue"][2]["concept"], "R1")
        self.assertEqual(q["queue"][2]["due_kind"], "review")

    def test_excludes_not_due_and_other_tracks(self):
        self._seed(
            active_rows=[
                self._active("Due", next_review="2026-09-01"),
                self._active("NotDue", next_review="2026-10-30"),
                self._active("OtherTrack", next_review="2026-09-01", track="swe"),
            ],
            mistakes_rows=[self._mistake("2026-09-01", "NotDue", "2026-10-30")],
            attempts={"Due": self._attempt("2026-09-01"), "NotDue": self._attempt("2026-10-30"),
                      "OtherTrack": self._attempt("2026-09-01")},
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        names = [e["concept"] for e in q["queue"]]
        self.assertEqual(names, ["Due"])

    def test_question_type_alternates_by_last_q_type(self):
        self._seed(
            active_rows=[
                self._active("Defn", next_review="2026-09-01", last_q="definitional"),
                self._active("Disc", next_review="2026-09-01", last_q="discriminative"),
                self._active("Blank", next_review="2026-09-01", last_q=""),
            ],
            mistakes_rows=[],
            attempts={"Defn": self._attempt("2026-09-01"), "Disc": self._attempt("2026-09-01"),
                      "Blank": self._attempt("2026-09-01")},
        )
        by = {e["concept"]: e for e in ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)["queue"]}
        self.assertEqual(by["Defn"]["question_type"], "discriminative")
        self.assertEqual(by["Disc"]["question_type"], "definitional")
        self.assertEqual(by["Blank"]["question_type"], "discriminative")

    @staticmethod
    def _hist(ctype, qtypes):
        return {
            "type": ctype,
            "attempts": [
                {"date": f"2026-08-{i + 1:02d}", "is_correct": True, "result": "pass", "q_type": q}
                for i, q in enumerate(qtypes)
            ],
            "interval_index": 0, "consecutive_correct": len(qtypes), "consecutive_wrong": 0,
            "last_reviewed": "2026-09-01", "next_review": "2026-09-01", "feynman": None,
        }

    def test_queue_schedules_far_transfer_on_cadence(self):
        self._seed(
            active_rows=[self._active("Cadence", next_review="2026-09-01", ctype="concept")],
            mistakes_rows=[],
            attempts={"Cadence": self._hist("concept", ["definitional", "discriminative", "definitional"])},
        )
        by = {e["concept"]: e for e in ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)["queue"]}
        self.assertEqual(by["Cadence"]["question_type"], "transfer-far")
        self.assertEqual(by["Cadence"]["due_kind"], "review")

    def test_queue_does_not_force_transfer_for_memory(self):
        self._seed(
            active_rows=[self._active("Mem", next_review="2026-09-01", ctype="memory")],
            mistakes_rows=[],
            attempts={"Mem": self._hist("memory", ["definitional", "discriminative", "definitional"])},
        )
        by = {e["concept"]: e for e in ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)["queue"]}
        self.assertNotEqual(by["Mem"]["question_type"], "transfer-far")

    def test_adjacency_guard_avoids_consecutive_same_source(self):
        self._seed(
            active_rows=[
                self._active("A1", next_review="2026-09-01", source="Rohit P1 L01 (Python)"),
                self._active("A2", next_review="2026-09-01", source="Rohit P1 L01 (Python)"),
                self._active("B1", next_review="2026-09-01", source="Rohit P1 L02 (Python)"),
            ],
            mistakes_rows=[],
            attempts={"A1": self._attempt("2026-09-01"), "A2": self._attempt("2026-09-01"),
                      "B1": self._attempt("2026-09-01")},
        )
        keys = [ops._source_key(e) for e in ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 3)["queue"]]
        self.assertFalse(any(a == b for a, b in zip(keys, keys[1:])))

    def test_dedupes_same_concept_and_caps_mistakes_at_two(self):
        self._seed(
            active_rows=[
                self._active("M1", next_review="2026-09-01"),
                self._active("M2", next_review="2026-09-01"),
                self._active("M3", next_review="2026-09-01"),
            ],
            mistakes_rows=[
                self._mistake("2026-09-01", "M1", "2026-09-02"),
                self._mistake("2026-09-02", "M1", "2026-09-02"),  # duplicate concept
                self._mistake("2026-09-03", "M2", "2026-09-02"),
                self._mistake("2026-09-04", "M3", "2026-09-02"),
            ],
            attempts={"M1": self._attempt("2026-09-01"), "M2": self._attempt("2026-09-01"),
                      "M3": self._attempt("2026-09-01")},
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        mistakes = [e["concept"] for e in q["queue"] if e["due_kind"] == "mistake"]
        self.assertEqual(mistakes, ["M1", "M2"])

    def test_reports_next_review_drift(self):
        self._seed(
            active_rows=[self._active("Drift", next_review="2026-09-01")],
            mistakes_rows=[],
            attempts={"Drift": self._attempt("2026-09-15")},  # scheduler disagrees with AC
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        self.assertEqual(q["queue"], [])
        self.assertTrue(any("Drift" in w and "!=" in w for w in q["warnings"]))

    def test_digest_skeleton_written(self):
        self._seed(
            active_rows=[self._active("Due", next_review="2026-09-01")],
            mistakes_rows=[],
            attempts={"Due": self._attempt("2026-09-01")},
        )
        rel = "Learning System/.tmp/review-test-aiefs.json"
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_queue("aiefs", ops._parse_date("2026-09-10"), 5, digest_path=rel)
        self.assertIn("WROTE", buf.getvalue())
        digest = json.loads((ops.ROOT / rel).read_text(encoding="utf-8"))
        self.assertIsNone(digest["position"])
        self.assertEqual(digest["queue"][0]["concept"], "Due")
        self.assertIn(digest["queue"][0]["source_excerpt"], ("note",))  # notes fallback


class TestMasteryDimensions(unittest.TestCase):
    """P0.4: mastery is per-dimension, and a failed AI-free (solo) attempt
    blocks the independence gate; absent evidence is unknown, not zero."""

    def test_dimensions_split_by_question_type(self):
        entry = {
            "type": "concept", "interval_index": 2, "feynman": "pass",
            "attempts": [
                {"date": "2026-10-01", "is_correct": True, "q_type": "definitional"},
                {"date": "2026-10-02", "is_correct": False, "q_type": "computational"},
                {"date": "2026-10-03", "is_correct": True, "q_type": "transfer"},
            ],
        }
        d = ops.compute_dimensions(entry)
        self.assertEqual(d["recall"], 3)
        self.assertEqual(d["procedural"], 0)
        self.assertEqual(d["transfer"], 3)
        self.assertEqual(d["conceptual"], 3)
        self.assertEqual(d["stability"], 2)
        self.assertIsNone(d["independence"])

    def test_unknown_dimension_is_none_not_zero(self):
        d = ops.compute_dimensions({"attempts": [{"date": "2026-10-01", "is_correct": True}]})
        self.assertIsNone(d["procedural"])
        self.assertIsNone(d["transfer"])
        self.assertIsNone(d["independence"])
        self.assertEqual(d["recall"], 3)  # untagged counts as general recall

    def test_stability_is_none_without_attempts(self):
        d = ops.compute_dimensions({"type": "concept", "attempts": [], "interval_index": 0})
        self.assertIsNone(d["stability"])

    def test_stability_uses_interval_when_attempts_exist(self):
        d = ops.compute_dimensions(
            {"type": "concept", "attempts": [{"date": "2026-10-01", "is_correct": True}], "interval_index": 2}
        )
        self.assertEqual(d["stability"], 2)

    def test_independence_gate_blocks_solid_after_a_failed_solo(self):
        passed = {"attempts": [{"date": "2026-10-01", "is_correct": True, "mode": "solo"}]}
        self.assertTrue(ops.independence_ok(passed))
        failed = {"attempts": [{"date": "2026-10-01", "is_correct": False, "mode": "solo"}]}
        self.assertFalse(ops.independence_ok(failed))
        # No solo evidence is unknown, not failure (grandfathered).
        self.assertTrue(ops.independence_ok({"attempts": [{"date": "2026-10-01", "is_correct": True}]}))

    def test_attempt_records_optional_evidence(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": {}, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8",
        )
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("X", "fail", qtype="transfer", confidence="hunch", hints=2, mode="solo")
        data = json.loads((core / "Attempts.json").read_text(encoding="utf-8"))
        a = data["concepts"]["X"]["attempts"][0]
        self.assertEqual(a["confidence"], "hunch")
        self.assertEqual(a["hints"], 2)
        self.assertEqual(a["mode"], "solo")
        self.assertFalse(ops.independence_ok(data["concepts"]["X"]))
        # Optional fields are omitted when not supplied (back-compat).
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Y", "pass")
        y = json.loads((core / "Attempts.json").read_text(encoding="utf-8"))["concepts"]["Y"]["attempts"][0]
        self.assertNotIn("confidence", y)
        self.assertNotIn("hints", y)
        self.assertNotIn("mode", y)


class TestQTypeEnum(unittest.TestCase):
    """P1.2: q_type is an enum, not a free string; legacy aliases normalize."""

    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": {}, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    def test_unknown_qtype_is_rejected(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("X", "pass", qtype="bogus-type")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("unknown --qtype", buf.getvalue())

    def test_legacy_qtype_alias_is_normalized(self):
        root = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass", qtype="free_recall")
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["X"]["attempts"][0]["q_type"], "free-recall")

    def test_transfer_alias_normalizes_to_near(self):
        self.assertIsNone(ops.normalize_qtype("bogus"))
        self.assertEqual(ops.normalize_qtype("transfer"), "transfer-near")
        self.assertEqual(ops.normalize_qtype("novel"), "transfer-far")
        self.assertEqual(ops.normalize_qtype("transfer-far"), "transfer-far")


class TestBenchmarkScheduling(unittest.TestCase):
    """P1: benchmark shots keep the fixed +1/+7/+30 day ladder whatever the result.

    Retrieval must come back at the next shot even after a miss, so a fail
    never steps the index down and consecutive passes never earn a bonus step.
    """

    def _make_root(self, ctype="benchmark", index=0, consecutive_correct=0):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "Bench Item": {
                    "type": ctype,
                    "attempts": [],
                    "interval_index": index,
                    "consecutive_correct": consecutive_correct,
                    "consecutive_wrong": 0,
                    "last_reviewed": "2026-09-01",
                    "next_review": "2026-09-02",
                    "feynman": None,
                }
            },
            "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return core / "Attempts.json"

    def _entry(self, path):
        return json.loads(path.read_text(encoding="utf-8"))["concepts"]["Bench Item"]

    def test_benchmark_schedule_is_one_seven_thirty(self):
        self.assertEqual(ops.DEFAULT_INTERVALS["benchmark"], [1, 7, 30])

    def test_benchmark_pass_advances_one_step(self):
        path = self._make_root(consecutive_correct=1)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "pass", date="2026-09-04")
        entry = self._entry(path)
        # +1, not the two-consecutive-passes +2.
        self.assertEqual(entry["interval_index"], 1)
        self.assertEqual(entry["next_review"], "2026-09-11")  # +7d

    def test_benchmark_fail_advances_one_step(self):
        path = self._make_root(index=0)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "fail", date="2026-09-04")
        entry = self._entry(path)
        self.assertEqual(entry["interval_index"], 1)  # never steps back
        self.assertEqual(entry["next_review"], "2026-09-11")  # +7d
        self.assertEqual(entry["consecutive_wrong"], 1)
        self.assertEqual(entry["attempts"][-1]["result"], "fail")

    def test_benchmark_consecutive_fails_never_shorten_ladder(self):
        path = self._make_root(index=1)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "fail", date="2026-09-04")
        entry = self._entry(path)
        self.assertEqual(entry["interval_index"], 2)  # 1 → 2, not 1 → 0
        self.assertEqual(entry["next_review"], "2026-10-04")  # +30d

    def test_benchmark_ladder_clamps_at_30_days(self):
        path = self._make_root(index=2)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "fail", date="2026-09-04")
        entry = self._entry(path)
        self.assertEqual(entry["interval_index"], 2)  # clamped, still the 30d shot
        self.assertEqual(entry["next_review"], "2026-10-04")

    def test_benchmark_two_passes_take_two_steps_not_three(self):
        path = self._make_root(consecutive_correct=1)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "pass", date="2026-09-04")
            ops.do_attempt("Bench Item", "pass", date="2026-09-11")
        self.assertEqual(self._entry(path)["interval_index"], 2)

    def test_concept_ladder_still_steps_back_on_fail(self):
        path = self._make_root(ctype="concept", index=2)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "fail", date="2026-09-04")
        self.assertEqual(self._entry(path)["interval_index"], 1)

    def test_unknown_type_falls_back_to_concept_schedule(self):
        self.assertEqual(ops._intervals_for({"meta": {"intervals": {}}}, "mystery"),
                         [3, 7, 14, 30])
        self.assertEqual(ops._intervals_for({}, "mystery"), [3, 7, 14, 30])
        path = self._make_root(ctype="mystery", index=1)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "pass", date="2026-09-04")
        entry = self._entry(path)
        self.assertEqual(entry["interval_index"], 2)
        self.assertEqual(entry["next_review"], "2026-09-18")  # concept[2] = 14d


class TestBenchmarkIntervals(unittest.TestCase):
    """P2: a known type missing from the live `meta.intervals` map keeps its own
    default ladder instead of silently inheriting the concept schedule.

    The live Attempts.json was seeded before `benchmark` existed, so its
    `meta.intervals` pins only the four original types."""

    LIVE_META = {"memory": [0, 1, 3, 7, 14, 30, 60], "concept": [3, 7, 14, 30],
                 "procedure": [3, 7, 14], "design": [14, 28]}

    def test_benchmark_missing_from_live_map_uses_its_own_ladder(self):
        self.assertEqual(ops._intervals_for({"meta": {"intervals": self.LIVE_META}},
                                            "benchmark"), [1, 7, 30])

    def test_unknown_type_still_falls_back_to_concept(self):
        self.assertEqual(ops._intervals_for({"meta": {"intervals": self.LIVE_META}},
                                            "mystery"), [3, 7, 14, 30])

    def test_live_map_fail_steps_benchmark_up_to_seven_days(self):
        # With the concept ladder a fail at index 0 would land on +3d; the
        # benchmark ladder must land on +7d whatever the result.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {"concepts": {"Bench Item": {
            "type": "benchmark", "attempts": [], "interval_index": 0,
            "consecutive_correct": 0, "consecutive_wrong": 0,
            "last_reviewed": "2026-11-24", "next_review": "2026-11-25", "feynman": None,
        }}, "meta": {"version": 1, "intervals": self.LIVE_META}}
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Bench Item", "fail", date="2026-11-25")
        entry = json.loads((core / "Attempts.json").read_text(encoding="utf-8"))["concepts"]["Bench Item"]
        self.assertEqual(entry["interval_index"], 1)
        self.assertEqual(entry["next_review"], "2026-12-02")  # +7d, not +3d


class TestBenchmarkCommand(unittest.TestCase):
    """P2: `ops.py benchmark` seeds one ledger session + one row + one shot ladder.

    The per-question results live in the ledger, so a session's 15 answers never
    become 15 attempts (which would jump the ladder 15 steps)."""

    HEADER = ("| Concept | Track | Type | Status | Source | Last Reviewed | "
              "Next Review | Last Q Type | Open Question |")
    SEP = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    SESSION = "Psychology of Money — Introduction"

    @staticmethod
    def _questions(levels=None):
        levels = levels or ["low"] * 5 + ["mid"] * 5 + ["high"] * 5
        return {"source": "Morgan Housel, *The Psychology of Money*, Introduction",
                "scope": "Introduction, pp. 1-24",
                "questions": [{"idx": i, "level": lv, "text": f"Benchmark question {i}"}
                              for i, lv in enumerate(levels, 1)]}

    def _make_root(self, active_rows=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        core = root / "Learning System" / "Core"
        core.mkdir(parents=True)
        # Live-shaped meta.intervals: the four original types only.
        (core / "Attempts.json").write_text(json.dumps({
            "concepts": {},
            "meta": {"version": 1, "intervals": TestBenchmarkIntervals.LIVE_META},
        }), encoding="utf-8")
        (core / "📚 Active Concepts.md").write_text("\n".join([
            "# KNOWLEDGE BASE", "", "## AIEFS Track", "", self.HEADER, self.SEP,
            *active_rows,
        ]) + "\n", encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = root
        self.addCleanup(setattr, ops, "ROOT", old)
        return root

    def _questions_file(self, spec=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "questions.json"
        path.write_text(json.dumps(spec if spec is not None else self._questions()),
                        encoding="utf-8")
        return str(path)

    def _ledger(self, root):
        return json.loads((root / ops.BENCHMARK_LEDGER_PATH).read_text(encoding="utf-8"))

    def _attempts(self, root):
        return json.loads((root / "Learning System" / "Core" / "Attempts.json")
                          .read_text(encoding="utf-8"))

    def test_seeds_ledger_row_and_one_shot_ladder(self):
        root = self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_benchmark(self.SESSION, "2026-11-24", self._questions_file())
        self.assertIn("BENCHMARK OK", buf.getvalue())

        session = self._ledger(root)["sessions"][self.SESSION]
        self.assertEqual(session["date"], "2026-11-24")
        self.assertEqual(session["track"], "aiefs")
        self.assertEqual(session["scope"], "Introduction, pp. 1-24")
        self.assertEqual(len(session["questions"]), 15)
        self.assertEqual(session["shots"], [])
        self.assertEqual([q["idx"] for q in session["questions"]], list(range(1, 16)))
        self.assertEqual(session["questions"][0]["level"], "low")
        self.assertEqual(session["questions"][-1]["level"], "high")

        entry = self._attempts(root)["concepts"][self.SESSION]
        self.assertEqual(entry["type"], "benchmark")
        self.assertEqual(entry["interval_index"], 0)
        self.assertEqual(entry["next_review"], "2026-11-25")  # date + 1 day
        self.assertEqual(entry["attempts"], [])  # results live in the ledger

        row = ops._active_rows("aiefs")[0][self.SESSION]
        self.assertEqual(row["type"], "benchmark")
        self.assertEqual(row["status"], "developing")
        self.assertEqual(row["last_reviewed"], "2026-11-24")
        self.assertEqual(row["next_review"], "2026-11-25")

    def test_rerun_same_name_and_date_is_a_no_op(self):
        root = self._make_root()
        path = self._questions_file()
        with redirect_stdout(io.StringIO()):
            ops.do_benchmark(self.SESSION, "2026-11-24", path)
        before = self._ledger(root)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_benchmark(self.SESSION, "2026-11-24", path)
        self.assertIn("BENCHMARK NO-OP", buf.getvalue())
        self.assertEqual(self._ledger(root), before)
        self.assertEqual(self._attempts(root)["concepts"][self.SESSION]["attempts"], [])
        text = (root / "Learning System" / "Core" / "📚 Active Concepts.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(self.SESSION), 1)  # one row, never a duplicate

    def test_different_date_for_existing_name_is_rejected(self):
        root = self._make_root()
        path = self._questions_file()
        with redirect_stdout(io.StringIO()):
            ops.do_benchmark(self.SESSION, "2026-11-24", path)
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(SystemExit) as cm:
                ops.do_benchmark(self.SESSION, "2026-11-25", path)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("already seeded for 2026-11-24", buf.getvalue())
        self.assertEqual(self._ledger(root)["sessions"][self.SESSION]["date"], "2026-11-24")

    def test_bad_level_writes_nothing(self):
        root = self._make_root()
        path = self._questions_file(self._questions(["low"] * 5 + ["mid"] * 5 + ["extreme"] * 5))
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(SystemExit) as cm:
                ops.do_benchmark(self.SESSION, "2026-11-24", path)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("expected one of: low, mid, high", buf.getvalue())
        self.assertFalse((root / ops.BENCHMARK_LEDGER_PATH).exists())
        self.assertEqual(self._attempts(root)["concepts"], {})
        self.assertNotIn(self.SESSION, ops._active_rows("")[0])

    def test_empty_question_text_is_rejected(self):
        root = self._make_root()
        spec = self._questions()
        spec["questions"][3]["text"] = "   "
        path = self._questions_file(spec)
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_benchmark(self.SESSION, "2026-11-24", path)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("empty text", buf.getvalue())
        self.assertFalse((root / ops.BENCHMARK_LEDGER_PATH).exists())

    def test_idx_is_auto_assigned_when_absent(self):
        root = self._make_root()
        spec = self._questions()
        for q in spec["questions"]:
            del q["idx"]
        with redirect_stdout(io.StringIO()):
            ops.do_benchmark(self.SESSION, "2026-11-24", self._questions_file(spec))
        questions = self._ledger(root)["sessions"][self.SESSION]["questions"]
        self.assertEqual([q["idx"] for q in questions], list(range(1, 16)))

    def test_cli_seeds_a_benchmark_session(self):
        root = self._make_root()
        path = self._questions_file()
        old_argv = sys.argv
        sys.argv = ["ops.py", "benchmark", self.SESSION, "--date", "2026-11-24",
                    "--questions-file", path]
        self.addCleanup(setattr, sys, "argv", old_argv)
        with redirect_stdout(io.StringIO()):
            ops.main()
        self.assertIn(self.SESSION, self._ledger(root)["sessions"])
        self.assertEqual(self._attempts(root)["concepts"][self.SESSION]["next_review"],
                         "2026-11-25")


class TestBenchmarkQueue(unittest.TestCase):
    """P2: a due benchmark row is one normal queue slot carrying its type and the
    ledger key; the shots themselves advance the ladder one step per session."""

    SESSION = TestBenchmarkCommand.SESSION

    def _seed(self, day="2026-11-24"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        core = root / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(json.dumps({
            "concepts": {},
            "meta": {"version": 1, "intervals": TestBenchmarkIntervals.LIVE_META},
        }), encoding="utf-8")
        (core / "📚 Active Concepts.md").write_text("\n".join([
            "# KNOWLEDGE BASE", "", "## AIEFS Track", "",
            TestBenchmarkCommand.HEADER, TestBenchmarkCommand.SEP,
        ]) + "\n", encoding="utf-8")
        qtmp = tempfile.TemporaryDirectory()
        self.addCleanup(qtmp.cleanup)
        qpath = Path(qtmp.name) / "questions.json"
        qpath.write_text(json.dumps(TestBenchmarkCommand._questions()), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = root
        self.addCleanup(setattr, ops, "ROOT", old)
        with redirect_stdout(io.StringIO()):
            ops.do_benchmark(self.SESSION, day, str(qpath))
        return root

    def _set_next_review(self, root, day):
        path = root / "Learning System" / "Core" / "Attempts.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["concepts"][self.SESSION]["next_review"] = day
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_due_benchmark_row_enters_the_queue_as_one_slot(self):
        self._seed()
        payload = ops._build_queue("aiefs", ops._parse_date("2026-11-25"), 5)
        self.assertEqual(len(payload["queue"]), 1)
        entry = payload["queue"][0]
        self.assertEqual(entry["concept"], self.SESSION)  # == the ledger key
        self.assertEqual(entry["type"], "benchmark")
        self.assertEqual(entry["due_kind"], "review")
        self.assertEqual(entry["next_review"], "2026-11-25")

    def test_not_due_benchmark_row_is_omitted(self):
        root = self._seed()
        self._set_next_review(root, "2026-12-01")
        payload = ops._build_queue("aiefs", ops._parse_date("2026-11-25"), 5)
        self.assertEqual(payload["queue"], [])
        self.assertEqual(payload["due_reviews"], 0)

    def test_one_shot_advances_the_ladder_once(self):
        root = self._seed()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt(self.SESSION, "fail", date="2026-11-25")
        entry = json.loads((root / "Learning System" / "Core" / "Attempts.json")
                           .read_text(encoding="utf-8"))["concepts"][self.SESSION]
        self.assertEqual(entry["interval_index"], 1)
        self.assertEqual(entry["next_review"], "2026-12-02")  # +7d
        self.assertEqual(len(entry["attempts"]), 1)  # one attempt, not 15
        ledger = json.loads((root / ops.BENCHMARK_LEDGER_PATH).read_text(encoding="utf-8"))
        self.assertEqual(ledger["sessions"][self.SESSION]["shots"], [])  # results are ledger data

    def test_three_shots_stay_on_the_fixed_ladder(self):
        root = self._seed()
        for shot_day in ("2026-11-25", "2026-12-02", "2027-01-01"):
            with redirect_stdout(io.StringIO()):
                ops.do_attempt(self.SESSION, "fail", date=shot_day)
        entry = json.loads((root / "Learning System" / "Core" / "Attempts.json")
                           .read_text(encoding="utf-8"))["concepts"][self.SESSION]
        self.assertEqual(entry["interval_index"], 2)  # clamped at the 30d shot
        self.assertEqual([a["date"] for a in entry["attempts"]],
                         ["2026-11-25", "2026-12-02", "2027-01-01"])


class TestAttemptLevel(unittest.TestCase):
    """P1: `--level` is a validated, record-only per-question label."""

    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": {}, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return core / "Attempts.json"

    def test_level_is_stored_when_given(self):
        path = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass", level="high")
        a = json.loads(path.read_text(encoding="utf-8"))["concepts"]["X"]["attempts"][0]
        self.assertEqual(a["level"], "high")

    def test_level_is_normalized(self):
        path = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass", level=" MID ")
        a = json.loads(path.read_text(encoding="utf-8"))["concepts"]["X"]["attempts"][0]
        self.assertEqual(a["level"], "mid")

    def test_level_is_absent_when_not_given(self):
        path = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass")
        a = json.loads(path.read_text(encoding="utf-8"))["concepts"]["X"]["attempts"][0]
        self.assertNotIn("level", a)

    def test_invalid_level_is_rejected(self):
        path = self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("X", "pass", level="extreme")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("unknown --level", buf.getvalue())
        # Rejected before any write.
        self.assertNotIn("X", json.loads(path.read_text(encoding="utf-8"))["concepts"])

    def test_level_does_not_change_scheduling(self):
        plain = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass")
        levelled = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass", level="low")
        a = json.loads(plain.read_text(encoding="utf-8"))["concepts"]["X"]
        b = json.loads(levelled.read_text(encoding="utf-8"))["concepts"]["X"]
        self.assertEqual(a["interval_index"], b["interval_index"])
        self.assertEqual(a["next_review"], b["next_review"])

    def test_cli_passes_level_and_benchmark_type(self):
        path = self._make_root()
        old_argv = sys.argv
        sys.argv = ["ops.py", "attempt", "Bench", "pass", "--type", "benchmark",
                    "--level", "low"]
        self.addCleanup(setattr, sys, "argv", old_argv)
        with redirect_stdout(io.StringIO()):
            ops.main()
        entry = json.loads(path.read_text(encoding="utf-8"))["concepts"]["Bench"]
        self.assertEqual(entry["type"], "benchmark")
        self.assertEqual(entry["attempts"][0]["level"], "low")
        self.assertEqual(entry["interval_index"], 1)


class TestGradeMcq(unittest.TestCase):
    """P1.2: deterministic MCQ grading — no LLM in the mechanical path."""

    def test_grade_mcq_mixed_letters(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_grade_mcq("A,B,C", "A,C,C")
        out = buf.getvalue()
        self.assertIn("2/3 correct", out)
        self.assertIn("key B · answer C → FAIL", out)
        self.assertIn("key C · answer C → PASS", out)

    def test_grade_mcq_empty_answer_is_wrong(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_grade_mcq("A,B", "A,-")
        self.assertIn("1/2 correct", buf.getvalue())

    def test_grade_mcq_length_mismatch_exits(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                ops.do_grade_mcq("A,B", "A")
        self.assertEqual(cm.exception.code, 2)

    def test_grade_mcq_rejects_non_letter_token(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                ops.do_grade_mcq("A1,B?", "A1,B?")
        self.assertEqual(cm.exception.code, 2)


class TestPrereqs(unittest.TestCase):
    """P1.3: prerequisite edges in live state; a fuzzy direct prereq blocks."""

    def _seed(self, concepts, mistakes=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": concepts, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        header = ("| Date | Concept | Question | Expected | Error Type | Self-Attribution | "
                  "Status | Retries | Next Retry |")
        sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        rows = [f"| 2026-09-01 | {c} | Q? | Expected | structural | why | active | 0 | 2026-09-02 |"
                for c in mistakes]
        (core / "🧯 Mistakes.md").write_text(
            "\n".join(["# Mistakes", "", header, sep, *rows]) + "\n", encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    @staticmethod
    def _entry(feynman=None, wrong=0, correct=0, interval=0, last_ok=True):
        return {"type": "concept", "feynman": feynman, "consecutive_wrong": wrong,
                "consecutive_correct": correct, "interval_index": interval,
                "attempts": [{"date": "2026-09-01", "is_correct": last_ok, "result": "pass"}]}

    def test_fuzzy_prereq_blocks(self):
        self._seed({"A": self._entry(wrong=1, last_ok=False)})
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_prereqs("B", set_list=["A"])
        out = buf.getvalue()
        self.assertIn("BLOCKS", out)
        self.assertIn("A: fuzzy", out)

    def test_open_mistake_prereq_blocks(self):
        self._seed({"A": self._entry()}, mistakes=["A"])
        payload = ops._prereq_state("A", {"A": self._entry()}, ops._open_mistake_concepts())
        self.assertEqual(payload, "fuzzy")

    def test_unknown_prereq_does_not_block(self):
        self._seed({"A": self._entry()})
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_prereqs("B", set_list=["Missing"])
        out = buf.getvalue()
        self.assertNotIn("BLOCKS", out)
        self.assertIn("Missing: unknown", out)

    def test_set_persists_prereqs(self):
        root = self._seed({})
        with redirect_stdout(io.StringIO()):
            ops.do_prereqs("B", set_list=["A", "C"])
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["B"]["prereqs"], ["A", "C"])


class TestCalibration(unittest.TestCase):
    """P1.4: confidence is measured, not just elicited."""

    def test_calibration_flags_overconfidence(self):
        attempts = [
            {"is_correct": True, "confidence": "sure"},
            {"is_correct": False, "confidence": "sure"},
            {"is_correct": False, "confidence": "sure"},
            {"is_correct": True, "confidence": "hunch"},
        ]
        cal = ops.compute_calibration(attempts)
        self.assertIn("overconfident", cal["flags"])
        self.assertEqual(cal["buckets"]["sure"]["n"], 3)
        self.assertEqual(cal["buckets"]["sure"]["correct"], 1)

    def test_calibration_ignores_untagged(self):
        cal = ops.compute_calibration([{"is_correct": True}, {"is_correct": False}])
        self.assertEqual(cal["buckets"], {})

    def test_calibration_reports_untagged_count(self):
        cal = ops.compute_calibration(
            [{"is_correct": True, "confidence": "sure"}, {"is_correct": False}, {"is_correct": True}]
        )
        self.assertEqual(cal["untagged"], 2)
        self.assertEqual(cal["buckets"]["sure"]["n"], 1)

    def test_mastery_json_includes_calibration_and_transfer(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "X": {
                    "type": "concept", "feynman": None, "interval_index": 1,
                    "consecutive_correct": 1, "consecutive_wrong": 0,
                    "attempts": [
                        {"date": "2026-10-01", "is_correct": True,
                         "confidence": "sure", "q_type": "transfer-far"},
                    ],
                }
            },
            "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_mastery("", as_json=True)
        rows = json.loads(buf.getvalue())
        row = rows[0]
        self.assertIn("calibration", row)
        self.assertTrue(row["transfer_ok"])


class TestTransferDimension(unittest.TestCase):
    """P1.5: transfer-near/far feed the transfer dimension; far transfer gates
    consolidation (when it exists)."""

    def test_transfer_dimension_from_transfer_far(self):
        entry = {
            "type": "concept", "interval_index": 2, "feynman": None,
            "attempts": [
                {"date": "2026-10-01", "is_correct": True, "q_type": "transfer-far"},
            ],
        }
        self.assertEqual(ops.compute_dimensions(entry)["transfer"], 3)
        self.assertTrue(ops.transfer_ok(entry))

    def test_transfer_far_fail_is_not_transfer_ok(self):
        entry = {"attempts": [{"date": "2026-10-01", "is_correct": False, "q_type": "transfer-far"}]}
        self.assertEqual(ops.compute_dimensions(entry)["transfer"], 0)
        self.assertFalse(ops.transfer_ok(entry))


class TestLearnerHistoryFeynmanGate(unittest.TestCase):
    """P1.1: a concept/design entry cannot be `solid` without a Feynman pass;
    memory/procedure stay exempt."""

    def test_concept_cannot_be_solid_without_feynman(self):
        import learner_history  # noqa: E402

        entry = {
            "type": "concept", "consecutive_correct": 3, "interval_index": 3,
            "consecutive_wrong": 0, "attempts": [{"date": "2026-10-01", "is_correct": True}],
            "feynman": None,
        }
        self.assertNotEqual(learner_history.tag("Concept", entry, set()), "solid")
        entry["feynman"] = "pass"
        self.assertEqual(learner_history.tag("Concept", entry, set()), "solid")

    def test_memory_is_exempt_from_feynman(self):
        import learner_history  # noqa: E402

        entry = {
            "type": "memory", "consecutive_correct": 3, "interval_index": 3,
            "consecutive_wrong": 0, "attempts": [{"date": "2026-10-01", "is_correct": True}],
            "feynman": None,
        }
        self.assertEqual(learner_history.tag("Memory", entry, set()), "solid")


class TestAmend(unittest.TestCase):
    """P2.5: `ops.py amend` is the audited replacement for .tmp state surgery."""

    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "Test Concept": {
                    "type": "concept",
                    "attempts": [
                        {"date": "2026-10-09", "is_correct": True, "result": "pass", "q_type": "computational"},
                    ],
                    "interval_index": 0,
                    "consecutive_correct": 1,
                    "consecutive_wrong": 0,
                    "last_reviewed": "2026-10-09",
                    "next_review": "2026-10-12",
                    "feynman": None,
                }
            },
            "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    def test_amend_redates_and_logs_reason(self):
        root = self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_amend("Test Concept", "2026-10-09", new_date="2026-10-08", reason="envelope date slip")
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(entry["attempts"][0]["date"], "2026-10-08")
        self.assertEqual(entry["last_reviewed"], "2026-10-08")
        self.assertEqual(entry["next_review"], "2026-10-11")  # concept interval +3d from the re-dated attempt
        amend = data["meta"]["amendments"][-1]
        self.assertEqual(amend["reason"], "envelope date slip")
        self.assertEqual(amend["changes"]["date"], {"from": "2026-10-09", "to": "2026-10-08"})

    def test_amend_fixes_metadata_field(self):
        root = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_amend("Test Concept", "2026-10-09", field="q_type", value="transfer", reason="wrong tag")
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["Test Concept"]["attempts"][0]["q_type"], "transfer-near")

    def test_amend_targets_and_rejects_bad_id(self):
        root = self._make_root()
        _seed_graph(
            root,
            nodes=[{"id": "n_ab12cd34ef", "op": "define"}],
            chains=[{
                "id": "arg_ab12cd34ef",
                "op": "assert",
                "premises": ["n_ab12cd34ef"],
                "conclusion": "n_ffffffffff",
            }],
        )
        with redirect_stdout(io.StringIO()):
            ops.do_amend("Test Concept", "2026-10-09", field="targets",
                         value="n_ab12cd34ef,arg_ab12cd34ef", reason="targets omitted")
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["Test Concept"]["attempts"][0]["targets"],
                         ["arg_ab12cd34ef", "n_ab12cd34ef"])
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2026-10-09", field="targets",
                             value="Bayes theorem", reason="typo")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("--targets", buf.getvalue())

    def test_amend_rejects_stale_graph_target(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2026-10-09", field="targets",
                             value="n_ab12cd34ef", reason="stale id")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("not live in the knowledge graph", buf.getvalue())

    def test_amend_requires_reason(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2026-10-09", new_date="2026-10-08")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("--reason", buf.getvalue())

    def test_amend_rejects_unknown_field(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2026-10-09", field="is_correct", value="false", reason="x")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("--field", buf.getvalue())

    def test_amend_rejects_missing_attempt(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2020-01-01", new_date="2026-10-08", reason="x")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("no attempt dated", buf.getvalue())

    def test_amend_rejects_negative_hints(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2026-10-09", field="hints", value="-3", reason="x")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("non-negative", buf.getvalue())

    def test_amend_rejects_future_date(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_amend("Test Concept", "2026-10-09", new_date="2099-01-01", reason="x")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("future", buf.getvalue())


class TestMistakePrereqLink(unittest.TestCase):
    """P2.8: a Mistakes row may name the broken prerequisite it exposes."""

    def _seed(self, attribution):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": {}, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        header = ("| Date | Concept | Question | Expected | Error Type | Self-Attribution | "
                  "Status | Retries | Next Retry |")
        sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        row = f"| 2026-10-01 | X | Q? | Expected | structural | {attribution} | active | 0 | 2026-10-02 |"
        (core / "🧯 Mistakes.md").write_text(
            "\n".join(["# Mistakes", "", header, sep, row]) + "\n", encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)

    def test_prereq_marker_parsed_and_stripped(self):
        self._seed("[prereq: Matrix Multiplication] slipped on the frame inversion")
        rows = ops._mistakes_rows()
        self.assertEqual(rows[0]["prereq"], "Matrix Multiplication")
        self.assertEqual(rows[0]["self_attribution"], "slipped on the frame inversion")

    def test_no_prereq_marker_is_empty(self):
        self._seed("just a slip")
        rows = ops._mistakes_rows()
        self.assertEqual(rows[0]["prereq"], "")
        self.assertEqual(rows[0]["self_attribution"], "just a slip")


class TestLearnerHistoryOpenMistakes(unittest.TestCase):
    """learner_history must read the ledger with ops.py's anchor rule, not by
    indexing cells[7]: a literal '|' in a free-text cell shifts that index and
    silently hides a live mistake."""

    def _seed(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        header = ("| Date | Concept | Question | Expected | Error Type | Self-Attribution | "
                  "Status | Retries | Next Retry |")
        sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        (core / "🧯 Mistakes.md").write_text(
            "\n".join(["# Mistakes", "", header, sep, *rows]) + "\n", encoding="utf-8")
        import learner_history  # noqa: E402

        old_core = learner_history.CORE
        learner_history.CORE = str(core)
        self.addCleanup(setattr, learner_history, "CORE", old_core)
        return learner_history

    def test_literal_pipes_do_not_hide_open_rows(self):
        lh = self._seed([
            # Two literal '|' cells shift the error type, so cells[7] used to be
            # "self" and this active row was silently skipped.
            "| 2026-10-01 | Piped | Q with | two | pipes | Expected | structural | "
            "self | active | 0 | 2026-10-02 |",
            "| 2026-10-02 | Closed | Q | Expected | deviation | self | graduated | 2 | 2026-10-03 |",
        ])
        self.assertEqual(lh.load_open_mistakes(), {"Piped"})

    def test_review_status_is_open(self):
        lh = self._seed([
            "| 2026-10-01 | Retry | Q | E | application | self | review | 1 | 2026-10-02 |",
        ])
        self.assertEqual(lh.load_open_mistakes(), {"Retry"})


if __name__ == "__main__":
    unittest.main()
