"""Pin the shared pi-subagents async run-id regex across the two languages.

The learning-gate adapter (TypeScript, inside pi) and the e2e runner (Python,
outside pi) each read the run id out of a pi-subagents completion notice. They
cannot share code: the cross-language seam is the wire format (ADR-0001), and
the two run in different processes. The regex is therefore duplicated on
purpose. This test fails when the copies stop agreeing, which is the drift a
pi-subagents upgrade would otherwise hide until an e2e run went blind.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TS_ADAPTER = ROOT / ".pi" / "extensions" / "learning-gate" / "pi-adapter" / "index.ts"
PY_RUNNER = ROOT / "harness" / "e2e-runner.py"

SAMPLE_URL = "async-subagent-runs/output-archives/0f8fad5b-d9cb-469f-a165-70867728950e"
SAMPLE_UUID = "0f8fad5b-d9cb-469f-a165-70867728950e"


def _ts_runid_literal() -> str:
    for line in TS_ADAPTER.read_text(encoding="utf-8").splitlines():
        marker = "text.match("
        if marker not in line:
            continue
        start = line.index(marker) + len(marker)
        end = line.rindex(")")
        literal = line[start:end].strip()
        if literal.startswith("/") and literal.endswith("/"):
            return literal[1:-1]
    raise AssertionError(f"no run-id regex found in {TS_ADAPTER}")


def _py_runid_literal() -> str:
    text = PY_RUNNER.read_text(encoding="utf-8")
    match = re.search(r'ASYNC_RUNID_RE\s*=\s*re\.compile\(\s*r"([^"]+)"', text)
    if not match:
        raise AssertionError(f"ASYNC_RUNID_RE not found in {PY_RUNNER}")
    return match.group(1)


class AsyncRunIdParity(unittest.TestCase):
    def test_the_two_languages_use_the_same_run_id_pattern(self):
        ts = _ts_runid_literal().replace(r"\/", "/")
        py = _py_runid_literal()
        self.assertEqual(
            ts,
            py,
            "pi-adapter and e2e-runner disagree on the async run-id regex; "
            "update both when pi-subagents changes the notice URL",
        )

    def test_the_shared_pattern_extracts_the_run_id(self):
        pattern = _ts_runid_literal().replace(r"\/", "/")
        match = re.search(pattern, SAMPLE_URL)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), SAMPLE_UUID)


if __name__ == "__main__":
    unittest.main()
