#!/usr/bin/env python3
"""Run the pi-bridge unittest suite and emit contract-coverage lines.

`test/contract/check_learning_layer.py` binds each contract invariant to passing
tests by matching `PASS <name>` lines. The deno gate suites already emit that
shape; this runner gives the bridge suite the same shape (one `PASS <test id>`
line per passing test) so bridge behavior is part of the same coverage corpus
without teaching the checker the (noisy, version-dependent) unittest -v format.

The standard unittest summary still goes to stderr, so `scripts/learn-check`
can report `Ran N tests`.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class _CoverageResult(unittest.TextTestResult):
    """A TextTestResult that also prints `PASS <test id>` per passing test."""

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

    def addSkip(self, test, reason: str) -> None:
        super().addSkip(test, reason)
        self._emit("SKIP", test)


def main() -> int:
    suite = unittest.TestLoader().discover(str(HERE), pattern="test_*.py")
    # verbosity=0 silences the runner's per-test dots: they are written to the
    # stream without a trailing newline and would prefix our `PASS` lines when
    # both streams share a file. printErrors + the "Ran N tests" summary still
    # go to the stream.
    runner = unittest.TextTestRunner(
        stream=sys.stderr, verbosity=0, resultclass=_CoverageResult
    )
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
