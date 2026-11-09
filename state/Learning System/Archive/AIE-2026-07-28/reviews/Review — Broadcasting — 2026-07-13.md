# Review — Broadcasting — 2026-07-13

**Date:** 2026-07-13
**Track:** aie
**Interval:** 3d → 3d (kept — mostly right)

## Question
What happens when you add a (4, 3) matrix and a (3,) vector in NumPy/PyTorch?

## Response
Vector expanded via broadcasting to (3, 3) to enable addition.

## Evaluation
Concept right (broadcasting stretches the smaller) but expanded shape is (4, 3), not (3, 3). Broadcasting aligns from right — the 3 matches, missing dim stretches to 4. Kept interval.

## Next Review: 2026-07-16
