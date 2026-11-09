# Review — Red-Green-Refactor — 2026-08-11

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (advanced)

**Question:** In TDD, you're supposed to see the test fail (Red) before writing code to make it pass (Green). What does seeing that failure first give you that a test written *after* the implementation can't?

**Answer:** Seeing Red proves the test (1) actually runs your code and (2) its assertion can catch a failure — no false positives. Skip Red and a passing test is a dead smoke detector.

**Assessment:** Correct — captured both the "test actually works" and "no false positives" points.

**Next Review:** 2026-08-18 (7d)
