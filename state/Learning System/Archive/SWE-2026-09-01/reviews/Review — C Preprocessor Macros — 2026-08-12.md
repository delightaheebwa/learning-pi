# Review — C Preprocessor Macros — 2026-08-12

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (advance)

**Question:** `#define SQUARE(x) ((x) * (x))` works until someone writes `SQUARE(++i)`. Why, and what's the general lesson about macros?

**Answer:** Macros are dumb text substitution — `SQUARE(++i)` becomes `((++i) * (++i))`, so `i` increments twice, silently. No types, no evaluation semantics, no error — the preprocessor can't see side effects.

**Assessment:** ✅ Solid. Got the mechanism (dumb find-and-replace, no error) and the lesson (no semantic awareness). Didn't spell out "incremented twice," but the substitution implies it.

**Next Review:** 2026-08-19 (7d)
