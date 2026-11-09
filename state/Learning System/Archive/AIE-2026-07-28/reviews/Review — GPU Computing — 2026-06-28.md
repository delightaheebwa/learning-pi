# Review — GPU Computing

**Date:** 2026-06-28
**Track:** AI Engineering (aie)
**Status:** developing — kept interval (3d reset)

## Result

Recalled the three GPU options (local, Colab, cloud) and correctly identified Tensor Cores as specialized matrix multiply hardware. However, the mechanism was fuzzy — Tensor Cores natively work on fp16/bf16, not "mixed precision" itself. Mixed precision (AMP) is the training strategy that orchestrates when to use fp16 vs fp32; Tensor Cores are the hardware that makes fp16 compute go fast.

## Action

Keep interval. Retest in 3 days.
