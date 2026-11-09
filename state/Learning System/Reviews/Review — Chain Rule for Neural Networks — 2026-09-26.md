# Review — Chain Rule for Neural Networks — 2026-09-26

- **Track/Source:** aiefs — Rohit P1 L05 + CS231n (Python)
- **Type:** procedure · **Q type:** computational
- **Why this slot:** due review 2026-09-26; first graded retrieval of the two-path chain rule since L05.
- **Question:** For f(x,y) = (x+y)·x² with u = x + y, z = x², compute df/dx = (∂f/∂u)(∂u/∂x) + (∂f/∂z)(∂z/∂x) at x = 2, y = 3.
- **Learner answer:** "2x(x+y)(x²+1)" — an unevaluated expression that multiplies the path contributions (evaluates to 100 at (2,3)).
- **Verdict:** FAIL — grade-audit agreed. Correct: via z: (x+y)(2x) = 5·4 = 20; via the direct x² factor (du/dx = 1): 4; total 24 (closed form 3x² + 2xy = 12 + 12).
- **Attempts.json:** mastery 0.50, interval_index 1, next_review 2026-10-03, Feynman: —
- **Mistakes ledger:** NEW 2026-09-26 row (error_type: application): the two path contributions were fused into one product instead of added — x appears in two places (u = x+y and z = x²), and each route gets its own additive contribution. The additive form IS the product rule g′h + gh′. Self-attribution inferred from the answer (x-appears-twice → corrections multiplied; learner wording not supplied). Next retry 2026-10-03.
- **Calibration:** repair delivered in-session with the nudge picture — one nudge of x changes f through both x-slots simultaneously and the changes add; the multiplicative fusion also fails the plug-in test (100 ≠ 24). Next probe planned: the nudge-y single-path contrast (df/dy = x² = 4).
