# Review — Sentinel Values vs Presence Flags — 2026-08-23

**Track:** SWE (monitor project)
**Question Type:** definitional (alternated from discriminative)
**Interval:** 7d → 14d (advance)

**Question:** Why is reusing the value `0` to mean "this field wasn't found" dangerous for a memory counter, and what should you use instead?

**Answer:** "0 to mean field not found doesnt give a clear picture of what actually happened. Use boolean flags instead."

**Assessment:** ✅ Pass. The key insight landed: 0 is ambiguous because it is also a VALID quantity (e.g. a legitimate zero-byte reading gets treated as "missing"); boolean presence flags (`has_total`) decouple structural presence from numeric payload. Advanced 7d → 14d.

**Next Review:** 2026-09-06 (14d)
