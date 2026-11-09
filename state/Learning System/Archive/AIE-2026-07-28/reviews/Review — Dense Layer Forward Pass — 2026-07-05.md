# Review — Dense Layer Forward Pass
**Date:** 2026-07-05
**Track:** AI Engineering (aie)
**Interval:** New → 3d

## Result: ⚠️ Mostly right — First review, set to 3d

**Prompt (after hint):** Write out the full mathematical expression for a single dense forward pass, including ReLU. Name each term and its dimensions.

**Response:**
- `relu(Wx + b)` — correct formula ✅
- W is weights ✅
- x is input
- b is bias

**Follow-up on dimensions (512→256):**
- x is (512,) — thought it was 512×256 ❌
- W is (256, 512) ✅
- b is a 1D array — correct, shape (256,) ✅

**Evaluation:** Got the formula right after a hint. Understood W@x+b conceptually but reversed the input dimensions. Setting to 3d interval.

**Next review:** 2026-07-08
