# Review — Gradient Accumulation (+=) — 2026-07-14

**Track:** aie
**Interval:** Reset to 3d
**Result:** Wrong — gave a vague answer about "hindering training." Technical reason: multivariable chain rule sums gradient contributions from all paths. Using `=` overwrites, silently dropping all but the last. `+=` ensures every path is counted.
**Next Review:** 2026-07-17
