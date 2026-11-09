# Review — Forward-Mode Autodiff — 2026-07-11

- **Track:** AI Engineering (aie)
- **Session:** 2026-07-11 — AIE Review Session
- **Result:** ✅ Fully correct
- **Interval:** 3d → 7d

## Question Asked
"What use case makes forward-mode autodiff the right choice over reverse-mode?"

## User's Answer
"In sensitivity analysis where you try to see the effect on many output variables when you tweak a few input variables. Forward mode autodiff is best with cases where you have few inputs and many outputs."

## Assessment
Correct. Forward-mode costs O(n) passes for n inputs; reverse-mode costs O(m) for m outputs. When n << m (few inputs, many outputs), forward-mode wins. Sensitivity analysis is the textbook use case. Advanced to 7d.
