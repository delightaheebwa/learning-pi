# Review — GPU Computing — 2026-07-08

**Date:** 2026-07-08
**Track:** aie
**Interval status:** Kept

## Question
What does Tensor Core precision mean for a training loop? One sentence — when would you *not* use fp16?

## Response
fp16 is for speed. (After correction: acknowledged fp16 is the fast path for the heavy matmul.)

## Evaluation
Mostly right after correction — had the direction backward (said don't use fp16 for grunt work, but that's exactly what Tensor Cores accelerate). Diagnostic confirmed it was a terminology slip, not conceptual.

## Next Review: 2026-07-13
