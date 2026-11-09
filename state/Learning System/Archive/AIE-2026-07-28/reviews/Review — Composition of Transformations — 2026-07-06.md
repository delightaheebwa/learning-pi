# Review — Composition of Transformations — 2026-07-06

**Track:** AI Engineering (aie)
**Interval:** First review → **3d**
**Next Review:** 2026-07-09

## Question
If you have two transformation matrices S (scale by 2) and R (rotate 90°), and you write S @ R (applied as (S @ R) @ v), which happens first — rotation or scale?

## Response
"Rotation happens first and then the scale."

## Follow-up
What happens if you swap the order to R @ S? Result stays the same?

## Response
Correctly identified that matrix multiplication is not commutative — S @ R ≠ R @ S.

## Evaluation
Fully correct on both points.

**Result:** Advanced to 3d.
