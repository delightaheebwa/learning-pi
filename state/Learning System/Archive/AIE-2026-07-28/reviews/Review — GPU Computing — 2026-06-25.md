# Review — GPU Computing

**Date:** 2026-06-25
**Status:** ⏸️ Kept current interval (nuance missed)

## What was asked
Three GPU options for AI work + fp16 precision and its relationship to Tensor Cores.

## User's answer
- Options: local GPU, Colab GPU, cloud GPU ✓
- fp16/Tensor Cores: "approximate model size by getting fp16 divided by number of tensor cores" ✗

## Evaluation
**Mostly right on the options, wrong on fp16/Tensor Cores.**
- Three GPU options are correct (local NVIDIA, Google Colab T4, cloud GPU)
- fp16 means 2 bytes per parameter (half of fp32's 4 bytes) — memory formula is `params × bytes_per_param`
- Tensor Cores accelerate mixed-precision compute — they don't determine memory capacity

## Action
Kept current interval (next review: 2026-06-28).
