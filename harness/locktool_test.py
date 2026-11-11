"""Unit tests for harness/locktool.py (the versions.lock.json helper).

Pure helpers, so nothing here reads or writes the real versions.lock.json:
every test owns a TemporaryDirectory and a throwaway lock file inside it.
Run with: python3 -m unittest discover -s harness -p '*_test.py'
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
from unittest import mock

LOCKTOOL_PATH = Path(__file__).with_name("locktool.py")


def load_locktool():
    spec = importlib.util.spec_from_file_location("locktool", LOCKTOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


locktool = load_locktool()


class LocktoolTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.lock = Path(self._tmp.name) / "versions.lock.json"

    def write_lock(self, data):
        self.lock.write_text(json.dumps(data), encoding="utf-8")

    def read_lock(self):
        return json.loads(self.lock.read_text(encoding="utf-8"))

    def capture(self, func, *args):
        """Run func(*args), returning (stdout, return_value)."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = func(*args)
        return buf.getvalue(), result

    def capture_stderr(self, func, *args):
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            result = func(*args)
        return buf.getvalue(), result


class CmdGetTest(LocktoolTestCase):
    def setUp(self):
        super().setUp()
        self.write_lock(
            {
                "pi": "1.4.2",
                "packages": {"alpha": "0.9.0", "beta": "2.0.1"},
            }
        )

    def test_get_pi_key(self):
        out, _ = self.capture(locktool.cmd_get, str(self.lock), "pi")
        self.assertEqual(out, "1.4.2\n")

    def test_get_package_key(self):
        out, _ = self.capture(locktool.cmd_get, str(self.lock), "beta")
        self.assertEqual(out, "2.0.1\n")

    def test_get_missing_key_prints_empty_line(self):
        out, _ = self.capture(locktool.cmd_get, str(self.lock), "gamma")
        self.assertEqual(out, "\n")

    def test_get_missing_pi_key_prints_empty_line(self):
        self.write_lock({"packages": {"alpha": "0.9.0"}})
        out, _ = self.capture(locktool.cmd_get, str(self.lock), "pi")
        self.assertEqual(out, "\n")

    def test_get_tolerates_null_packages(self):
        self.write_lock({"pi": "1.4.2", "packages": None})
        out, _ = self.capture(locktool.cmd_get, str(self.lock), "alpha")
        self.assertEqual(out, "\n")


class CmdPackagesTest(LocktoolTestCase):
    def test_lists_every_package_as_name_equals_version(self):
        self.write_lock({"pi": "1.4.2", "packages": {"alpha": "0.9.0", "beta": "2.0.1"}})
        out, _ = self.capture(locktool.cmd_packages, str(self.lock))
        self.assertEqual(out, "alpha=0.9.0\nbeta=2.0.1\n")

    def test_no_packages_prints_nothing(self):
        self.write_lock({"pi": "1.4.2"})
        out, _ = self.capture(locktool.cmd_packages, str(self.lock))
        self.assertEqual(out, "")


class CmdPromoteTest(LocktoolTestCase):
    def test_promote_updates_pi_merges_packages_and_appends_journal(self):
        self.write_lock(
            {"pi": "1.4.2", "packages": {"alpha": "0.9.0", "beta": "2.0.1"}}
        )
        out, _ = self.capture(
            locktool.cmd_promote,
            str(self.lock),
            "promote",
            "1.4.2",
            "1.5.0",
            '{"alpha": "0.9.0"}',
            '{"alpha": "1.0.0", "gamma": "3.2.0"}',
        )
        self.assertEqual(out, "")
        data = self.read_lock()
        self.assertEqual(data["pi"], "1.5.0")
        self.assertEqual(
            data["packages"],
            {"alpha": "1.0.0", "beta": "2.0.1", "gamma": "3.2.0"},
        )
        self.assertEqual(len(data["journal"]), 1)
        entry = data["journal"][0]
        self.assertRegex(entry["at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(entry["action"], "promote")
        self.assertEqual(entry["piFrom"], "1.4.2")
        self.assertEqual(entry["piTo"], "1.5.0")
        self.assertEqual(entry["packagesFrom"], {"alpha": "0.9.0"})
        self.assertEqual(entry["packagesTo"], {"alpha": "1.0.0", "gamma": "3.2.0"})
        self.assertEqual(
            set(entry),
            {"at", "action", "piFrom", "piTo", "packagesFrom", "packagesTo"},
        )

    def test_promote_preserves_existing_journal_entries(self):
        earlier = {
            "at": "2026-10-01T00:00:00Z",
            "action": "rollback",
            "piFrom": "1.5.0",
            "piTo": "1.4.2",
            "packagesFrom": {"alpha": "1.0.0"},
            "packagesTo": {"alpha": "0.9.0"},
        }
        self.write_lock(
            {"pi": "1.4.2", "packages": {"alpha": "0.9.0"}, "journal": [earlier]}
        )
        self.capture(
            locktool.cmd_promote,
            str(self.lock),
            "rollback",
            "1.4.2",
            "1.3.0",
            '{"alpha": "0.9.0"}',
            "{}",
        )
        data = self.read_lock()
        self.assertEqual(len(data["journal"]), 2)
        self.assertEqual(data["journal"][0], earlier)
        self.assertEqual(data["journal"][1]["action"], "rollback")
        self.assertEqual(data["journal"][1]["piTo"], "1.3.0")
        self.assertEqual(data["pi"], "1.3.0")
        self.assertEqual(data["packages"], {"alpha": "0.9.0"})

    def test_promote_with_empty_inputs_keeps_current_pi_and_packages(self):
        self.write_lock({"pi": "1.4.2", "packages": {"alpha": "0.9.0"}})
        self.capture(
            locktool.cmd_promote, str(self.lock), "promote", "", "", "", ""
        )
        data = self.read_lock()
        self.assertEqual(data["pi"], "1.4.2")
        self.assertEqual(data["packages"], {"alpha": "0.9.0"})
        self.assertEqual(len(data["journal"]), 1)
        entry = data["journal"][0]
        self.assertEqual(entry["piFrom"], "1.4.2")
        self.assertEqual(entry["piTo"], "1.4.2")
        self.assertEqual(entry["packagesFrom"], {})
        self.assertEqual(entry["packagesTo"], {})


class CmdLastPromotionTest(LocktoolTestCase):
    def test_returns_last_promote_or_rollback_entry_as_json(self):
        first = {"at": "2026-10-01T00:00:00Z", "action": "promote", "piTo": "1.4.2"}
        last = {"at": "2026-10-02T00:00:00Z", "action": "rollback", "piTo": "1.3.0"}
        note = {"at": "2026-10-03T00:00:00Z", "action": "note"}
        self.write_lock({"pi": "1.3.0", "journal": [first, last, note]})
        out, _ = self.capture(locktool.cmd_last_promotion, str(self.lock))
        self.assertEqual(out, json.dumps(last) + "\n")

    def test_empty_line_when_journal_has_no_promotions(self):
        self.write_lock({"pi": "1.3.0", "journal": [{"action": "note"}]})
        out, _ = self.capture(locktool.cmd_last_promotion, str(self.lock))
        self.assertEqual(out, "\n")

    def test_empty_line_when_journal_is_absent(self):
        self.write_lock({"pi": "1.3.0"})
        out, _ = self.capture(locktool.cmd_last_promotion, str(self.lock))
        self.assertEqual(out, "\n")


class MainTest(LocktoolTestCase):
    def setUp(self):
        super().setUp()
        self.write_lock({"pi": "1.4.2", "packages": {"alpha": "0.9.0"}})

    def test_unknown_command_returns_2(self):
        argv = ["locktool.py", "bogus", str(self.lock)]
        with mock.patch.object(sys, "argv", argv):
            err, code = self.capture_stderr(locktool.main)
        self.assertEqual(code, 2)
        self.assertEqual(err, "unknown command: bogus\n")

    def test_get_command_returns_0_and_prints_pinned_version(self):
        argv = ["locktool.py", "get", str(self.lock), "pi"]
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", argv):
            with contextlib.redirect_stdout(buf):
                code = locktool.main()
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue(), "1.4.2\n")


if __name__ == "__main__":
    unittest.main()
