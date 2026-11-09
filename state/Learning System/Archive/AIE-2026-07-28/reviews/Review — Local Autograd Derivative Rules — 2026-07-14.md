# Review — Local Autograd Derivative Rules — 2026-07-14

**Track:** aie
**Interval:** Reset to 3d
**Result:** Wrong — confused add and mul backward rules. Said da/dc = b (that's multiply). For add: ∂c/∂a = 1, ∂c/∂b = 1. Add passes gradient through, multiply crosses inputs.
**Next Review:** 2026-07-17
