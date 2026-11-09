#!/usr/bin/env python3
"""Regression tests for scripts/wiki_provenance.py — stdlib only.

Run: python3 -m unittest scripts.wiki_provenance_test
     (or: python3 scripts/wiki_provenance_test.py)

Guards the P0.6 provenance lint: an unknown status, a self-declared `verified`
with no source/verifier/date, or a marker buried mid-file must fail `--check`
rather than pass as trusted.
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiki_provenance as wp  # noqa: E402


class TestMarkerParsing(unittest.TestCase):
    def test_unknown_status_is_returned_raw_not_coerced(self):
        text = "<!-- provenance: status=bogus | source=x | verified-by=y | date=2026-10-08 -->\n\nBody"
        self.assertEqual(wp.read_status(text), "bogus")
        self.assertIn("unknown status", wp.marker_problem(text))

    def test_missing_marker_is_a_problem(self):
        self.assertIsNone(wp.read_status("No marker here."))
        self.assertEqual(wp.marker_problem("No marker here."), "missing marker")

    def test_verified_requires_source_verifier_and_date(self):
        bare = "<!-- provenance: status=verified | source=legacy | verified-by=— | date=2026-10-08 -->\n"
        self.assertEqual(wp.marker_problem(bare), "status=verified requires verified-by")
        no_date = "<!-- provenance: status=verified | source=ref | verified-by=alice -->\n"
        self.assertEqual(wp.marker_problem(no_date), "status=verified requires a valid date=YYYY-MM-DD")
        complete = "<!-- provenance: status=verified | source=ref | verified-by=alice | date=2026-10-08 -->\n"
        self.assertIsNone(wp.marker_problem(complete))

    def test_marker_must_be_in_the_first_lines(self):
        body = "\n".join(["# Title"] + ["prose"] * 10)
        mid = body + "\n<!-- provenance: status=unverified | source=legacy | verified-by=— | date=2026-10-08 -->\n"
        self.assertEqual(wp.marker_problem(mid), "missing marker")
        top = "<!-- provenance: status=unverified | source=legacy | verified-by=— | date=2026-10-08 -->\n" + body
        self.assertIsNone(wp.marker_problem(top))

    def test_unverified_and_synthesis_need_no_evidence(self):
        self.assertIsNone(wp.marker_problem("<!-- provenance: status=unverified -->\n"))
        self.assertIsNone(wp.marker_problem("<!-- provenance: status=synthesis | source=x -->\n"))


class TestScanCheck(unittest.TestCase):
    def _with_wiki(self, pages: dict):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        wiki = Path(tmp.name) / "Knowledge Wiki" / "wiki"
        wiki.mkdir(parents=True)
        for name, text in pages.items():
            (wiki / name).write_text(text, encoding="utf-8")
        old = wp.WIKI_DIR
        wp.WIKI_DIR = wiki
        self.addCleanup(setattr, wp, "WIKI_DIR", old)
        return wiki

    def test_scan_reports_invalid_and_missing_separately(self):
        self._with_wiki(
            {
                "good.md": "<!-- provenance: status=unverified -->\n\nbody",
                "bad.md": "<!-- provenance: status=verified | source=legacy | verified-by=— -->\n",
                "none.md": "no marker",
            }
        )
        report = wp.scan()
        self.assertEqual(report["counts"]["unverified"], 1)
        self.assertEqual([i["file"] for i in report["invalid"]], ["bad.md"])
        self.assertEqual(report["missing"], ["none.md"])

    def test_check_exits_nonzero_on_invalid(self):
        self._with_wiki({"bad.md": "<!-- provenance: status=verified -->\n"})
        old_argv = sys.argv
        sys.argv = ["wiki_provenance.py", "--check"]
        try:
            with redirect_stdout(io.StringIO()):
                code = wp.main()
        finally:
            sys.argv = old_argv
        self.assertEqual(code, 1)

    def test_main_check_fails_on_invalid(self):
        self._with_wiki({"bad.md": "<!-- provenance: status=verified -->\n"})
        old_argv = sys.argv
        sys.argv = ["wiki_provenance.py", "--check"]
        try:
            with redirect_stdout(io.StringIO()):
                code = wp.main()
        finally:
            sys.argv = old_argv
        self.assertEqual(code, 1)

    def test_main_check_passes_on_valid(self):
        self._with_wiki({"ok.md": "<!-- provenance: status=unverified -->\n\nbody"})
        old_argv = sys.argv
        sys.argv = ["wiki_provenance.py", "--check"]
        try:
            with redirect_stdout(io.StringIO()):
                code = wp.main()
        finally:
            sys.argv = old_argv
        self.assertEqual(code, 0)


class TestJsonReport(unittest.TestCase):
    def test_json_report_shape(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        wiki = Path(tmp.name) / "Knowledge Wiki" / "wiki"
        wiki.mkdir(parents=True)
        (wiki / "a.md").write_text("<!-- provenance: status=unverified -->\n", encoding="utf-8")
        old = wp.WIKI_DIR
        wp.WIKI_DIR = wiki
        self.addCleanup(setattr, wp, "WIKI_DIR", old)
        report = wp.scan()
        self.assertEqual(
            set(report.keys()), {"total", "counts", "missing", "invalid"}
        )
        self.assertEqual(report["total"], 1)
        json.dumps(report)  # serialisable


if __name__ == "__main__":
    unittest.main()
