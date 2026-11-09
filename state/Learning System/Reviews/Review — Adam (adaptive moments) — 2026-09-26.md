# Review — Adam (adaptive moments) — 2026-09-26

- **Track/Source:** aiefs — Rohit P1 L08 + Kingma & Ba 2015 + Ruder + handwritten notes 2026-09-08 (Python)
- **Type:** procedure · **Q type:** computational (free recall)
- **Why this slot:** due review 2026-09-26; first graded retrieval of the m/√v machinery since L08.
- **Question:** On paper: gradient g = +0.001 on both steps (t = 1, 2), β₁ = 0.9, β₂ = 0.999, lr = 1 — compute bias-corrected m̂₂, v̂₂, and the resulting parameter step.
- **Learner answer:** (skipped during the batch; stated afterwards: "i didnt know the answer")
- **Verdict:** FAIL — metacognitive, logged before the in-session repair (grade-audit not dispatched for an unanswered item; learner's own words).
- **Attempts.json:** mastery 0.50, interval_index 1, consecutive_wrong 1, next_review 2026-10-03, Feynman: —
- **Mistakes ledger:** NEW 2026-09-26 row (error_type: metacognitive, retries 0, next retry 2026-10-03); self-attribution is the learner's own words.
- **Calibration:** repair delivered in-session (fact-checked PASS): m = smoothed direction (0.9 old + 0.1 new), v = smoothed |g|² (typical size, sign erased); both averages START at zero so early estimates are only a fraction of the way home — divide by that fraction: m̂₂ = 0.00019/(1−0.81) = 0.001; v̂₂ = 1.999e−9/(1−0.998001) = 1e−6; step = 0.001/√1e−6 = 1.0 × lr. Units: m̂/√v̂ is dimensionless (gradient units over gradient units) ≈ ±1 — Adam asks only which SIGN and steps by fixed lr (scale-invariance, sign-descent behavior). Next probe 2026-10-03: the same fresh numbers, then read back why the hats exist.
