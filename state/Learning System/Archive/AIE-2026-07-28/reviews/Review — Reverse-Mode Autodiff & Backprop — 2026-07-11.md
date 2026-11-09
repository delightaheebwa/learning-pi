# Review — Reverse-Mode Autodiff & Backprop — 2026-07-11

- **Track:** AI Engineering (aie)
- **Session:** 2026-07-11 — AIE Review Session (Part 2)
- **Result:** ✅ Fully correct
- **Interval:** 3d → 7d

## Question Asked
"How many backward passes does reverse-mode autodiff need to compute all gradients for a neural net with a scalar loss?"

## User's Answer
"It needs just one"

## Assessment
Correct. One backward pass for a scalar loss. Compared to forward-mode's O(n) passes for n inputs, reverse-mode is O(1). This is why neural nets (millions of weights, one loss) exclusively use reverse-mode. Advanced to 7d.
