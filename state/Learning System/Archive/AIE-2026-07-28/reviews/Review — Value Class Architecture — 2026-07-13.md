# Review — Value Class Architecture — 2026-07-13

**Date:** 2026-07-13
**Track:** aie
**Interval:** 3d → 7d (advanced — correct)

## Question
What do _prev and _backward represent in the Value class?

## Response
_prev = children. _backward = pushing gradients from parent to children.

## Evaluation
_prev correct (set of child operands). _backward described the behavior correctly (gradients flowing to children) — it's a closure computing the local derivative and accumulating into _prev nodes via +=. Correct.

## Next Review: 2026-07-20
