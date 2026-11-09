# Review — Testable Seam — 2026-08-12

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (advance)

**Question:** Design A `read_meminfo()` opens `/proc/meminfo` itself; design B `parse_meminfo(text, out)` takes a string. Test asserts on `MemTotal`, fails on CI. Which fixes it, and what's the one-line change if you wrote A?

**Answer:** B — tests feed stable fixture text instead of live OS values. Change A to `read_meminfo(text, out)`: take the text as a parameter, push the file-opening out of the pure parse.

**Assessment:** ✅ Correct. Nailed both the choice and the refactor — seam = separating I/O from pure logic.

**Next Review:** 2026-08-19 (7d)
