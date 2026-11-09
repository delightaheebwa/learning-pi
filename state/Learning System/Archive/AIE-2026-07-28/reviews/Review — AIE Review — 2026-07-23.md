# Review — AIE Review — 2026-07-23

**Date:** 2026-07-23
**Session Type:** Spaced Repetition Review
**Track:** aie (AI Engineering — Micrograd)

## Concepts Reviewed (5/7 overdue, cap 5)

| Concept | Verdict | Previous Interval | New Interval | Next Review |
|---|---|---|---|---|
| Gradient Checking | Correct → advance | 3d | 7d | 2026-07-30 |
| Neural Network Training Loop | Correct → advance | 3d | 7d | 2026-07-30 |
| Micrograd Architecture | Correct (missed Layer) → keep | 3d | 3d | 2026-07-26 |
| Numerical vs Analytical Derivatives | Correct (nuance fix: swapped speed tradeoff) → advance | 7d | 14d | 2026-08-06 |
| Gradient Descent from Scratch | **Wrong** (used += instead of -=, added out.grad) → reset | 7d | 3d | 2026-07-26 |

## Key Takeaways

- Gradient descent update: `p.data -= lr * p.grad` — no `out.grad`, direction is `-=` (downhill)
- Micrograd chain: MLP → Layer → Neuron → Value (Layer is the missing piece)
- Analytical = exact + fast; Numerical = approximate + slow — the speed tradeoff was reversed in memory
- Gradient checking uses central difference `(f(x+h)-f(x-h))/(2h)` with h=1e-7, O(h²) error

## Not Reviewed (still overdue)

- Forward-Mode Autodiff (2026-07-18)
- Value Class Architecture (2026-07-20)
