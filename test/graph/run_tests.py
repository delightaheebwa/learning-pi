#!/usr/bin/env python3
"""Run the graph-ledger suite and emit contract-coverage lines.

`check_learning_layer.py` binds each invariant to passing tests by matching
`PASS <name>` lines. This runner gives the graph suite the same shape the gate
and bridge suites already emit, so graph behavior joins the same corpus.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class _CoverageResult(unittest.TextTestResult):
    def _emit(self, tag: str, test: unittest.case.TestCase) -> None:
        print(f"{tag} {test.id()}", flush=True)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self._emit("PASS", test)

    def addFailure(self, test, err) -> None:
        super().addFailure(test, err)
        self._emit("FAIL", test)

    def addError(self, test, err) -> None:
        super().addError(test, err)
        self._emit("FAIL", test)

    def addUnexpectedSuccess(self, test: unittest.case.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self._emit("FAIL", test)

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self._emit("SKIP", test)


def main() -> int:
    suite = unittest.TestLoader().discover(str(HERE), pattern="test_*.py")
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=0, resultclass=_CoverageResult)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
