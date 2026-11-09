# Review — Acutest Unit Testing — 2026-08-15

**Track:** SWE (C / Testing)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** What's the difference between `TEST_CHECK(expr)` and `TEST_ASSERT(expr)`, and why is `TEST_ASSERT`'s abort behavior safe inside a test?

**Answer:** TEST_CHECK lets a test fail while the rest of the suite keeps running; TEST_ASSERT aborts. The abort is safe when one test failing would corrupt the following tests.

**Assessment:** ⚠️ Partial. TEST_CHECK continues / TEST_ASSERT aborts — correct at the surface. But the safety mechanism was reversed: abort isn't safe because it prevents corruption — it's safe because **each test runs in its own child process**, so the OS reclaims everything on abort and the next test starts fresh in a new process. Process isolation is the load-bearing insight; "prevent cascade" is just the motivation for wanting an abort.

**Next Review:** 2026-08-18 (3d)
