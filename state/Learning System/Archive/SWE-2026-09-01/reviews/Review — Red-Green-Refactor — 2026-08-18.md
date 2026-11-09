# Review — Red-Green-Refactor — 2026-08-18

**Track:** SWE (Testing)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** In TDD you see the test fail (Red) *before* writing code to pass (Green). Why does Red matter — what two things does the initial failure prove, and what's the danger of skipping it?

**Answer:** Red proves the test actually works and can catch what it's supposed to catch. Skipping it risks false positives.

**Assessment:** ✅ Correct. The initial failure proves (1) the test actually runs the code you think it does, and (2) the assertion can catch a failure — no false positives. The danger of skipping Red is a "dead smoke detector": a test that passes even when the code is broken. User had the core idea right.

**Next Review:** 2026-09-01 (14d)
