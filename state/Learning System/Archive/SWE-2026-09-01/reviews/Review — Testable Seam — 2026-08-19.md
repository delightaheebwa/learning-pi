# Review — Testable Seam — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** Explain the Testable Seam — what it is, why it exists, and the concrete read_meminfo / parse_meminfo example.

**Answer (user):** The seam is a snapshot of the values to test; it exists because testing pure live data is brittle (ever-changing). Seam used on /proc/meminfo; read_meminfo gets the snapshot/picture, parse_meminfo extracts values and tests them.

**Assessment:** ⚠️ Partial. Correct on: brittleness of live data (why), the two-sided structure, and the seam substituting a controlled snapshot for the environment. **Correction — role assignment swapped:** `read_meminfo(path, out)` is the one that READS the live file (environment side); `parse_meminfo(text, out)` RECEIVES text and interprets it (pure logic side). It's the SEAM that swaps a fixed fixture string for what read would normally fetch, so parse can be tested against stable input. Clean framing: read = how you get data (hard to test); parse = what it means (deterministic, easy to test); bugs mostly live in parsing → most unit tests belong there. Core why was solid; role assignment needs a recheck.

**Next Review:** 2026-09-02 (14d)
