# Review — Parameter Expansion — 2026-08-08

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** When would you reach for `${var%pattern}` vs `${var#pattern}`? Give one example use for each.

**Answer:** `${var%pattern}` removes a matching **suffix** (e.g. `${FILE%.txt}` strips the extension); `${var#pattern}` removes a matching **prefix** (e.g. `${file##*/}` gives the basename).

**Assessment:** Miss — conflated `%`/`#` with value vs expression substitution. Neither is about that; both are prefix/suffix removal.

**Next Review:** 2026-08-11 (3d)
