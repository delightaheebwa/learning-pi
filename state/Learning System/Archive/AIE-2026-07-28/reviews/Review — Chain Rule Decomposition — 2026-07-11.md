# Review — Chain Rule Decomposition — 2026-07-11

- **Track:** AI Engineering (aie)
- **Session:** 2026-07-11 — AIE Review Session
- **Result:** ✅ Fully correct
- **Interval:** 3d → 7d

## Question Asked
"In one sentence: what two things does each node in backprop need to compute its gradient contribution?"

## User's Answer
"local derivative and upstream gradient"

## Assessment
Correct. Each node needs: (1) its own local derivative f'(x), and (2) the upstream gradient flowing back from later nodes. Gradient contribution = local derivative × upstream gradient. This is the chain rule decomposed into local operations. Advanced to 7d.
