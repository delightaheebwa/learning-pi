# Review — Broadcasting — 2026-07-06

**Track:** AI Engineering (aie)
**Interval:** 3d (kept)
**Next Review:** 2026-07-09

## Question
Why does W @ x + b work when W is a matrix, x is a vector, and b is a vector of a different size?

## Response
"It's because the broadcasting technique is applied to vector b which increases its rows via duplication to match the number of columns of the result of W @ x so that the operation is compatible."

## Evaluation
Core idea was right (broadcasting stretches b to match), but mechanism detail was off. Broadcasting aligns dimensions from the right, not from the left. If W@x gives (batch, n_units) and b is (n_units,), broadcasting aligns n_units with the last axis, then prepends a dimension and repeats along the batch axis. The user was thinking "match columns" (rightmost is the batch dim) which would be backward.

**Result:** Kept current interval (3d).
