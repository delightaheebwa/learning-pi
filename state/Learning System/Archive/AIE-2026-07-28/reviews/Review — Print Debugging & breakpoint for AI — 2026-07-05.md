# Review — Print Debugging & breakpoint for AI
**Date:** 2026-07-05
**Track:** AI Engineering (aie)
**Interval:** 3d → 3d (kept)

## Result: ⚠️ Partially right — Kept at 3d

**Prompt:** Describe how you'd build a debug_print utility for inspecting tensors in a training loop. What fields should it report, and how would you use breakpoint() conditionally inside the loop?

**Response:**
- debug_print for tensor shape, data transformations ✅
- breakpoint() when NaN is found ✅

**Evaluation:** Knew the use case for debug_print and conditional breakpoints on NaN. Missed the full field set (dtype, device, min/max/mean, NaN count). Also hadn't fully internalized the `p` command in pdb. Keeping current interval.

**Next review:** 2026-07-08
