# Review — Topological Sort for Backprop — 2026-07-13

**Date:** 2026-07-13
**Track:** aie
**Interval:** 3d → 7d (advanced — correct)

## Question
Why does backprop require reverse topological ordering?

## Response
Because it processes from outputs not inputs. Wrong order leads to wrong gradients.

## Evaluation
Correct. Key detail: guarantees every node receives all gradient contributions before propagating further. Wrong order = partial/zero gradients, silent bug.

## Next Review: 2026-07-20
