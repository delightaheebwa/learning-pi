# Review — Acutest Unit Testing — 2026-08-18

**Date:** 2026-08-18
**Next Review:** 2026-08-25 (7d)
**Q Type asked:** definitional

## Result: Mostly correct

- Process isolation → each test in its own child → OS reclaims resources on abort — ✅ core idea right.
- ⚠️ Scope correction: `TEST_ASSERT` aborts **that one test's child process**, NOT the whole suite. Parent runner records the failure and continues to the next test in a fresh child.
- Value of isolation: a hard `abort()` (for invariant/meaningless-to-continue states) is safe without killing or corrupting the rest of the suite.
- Contrast: `TEST_CHECK` logs the failure and lets the test continue (see multiple failures in one run); `TEST_ASSERT` stops this test.
- Anchor: **TEST_ASSERT = stop THIS test (abort child), suite continues. TEST_CHECK = log and keep going.**

## Interval
3d → 7d (advanced).
