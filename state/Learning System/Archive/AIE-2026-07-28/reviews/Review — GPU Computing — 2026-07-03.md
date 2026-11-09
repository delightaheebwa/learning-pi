# Review — GPU Computing

**Date:** 2026-07-03
**Track:** AI Engineering (aie)
**Concept:** GPU Computing
**Status:** developing — kept interval

## Performance

- Knew Tensor Cores are specialized for matrix multiplication
- Knew fp16 is used for speed
- **Slightly off:** Said Tensor Cores operate in fp32 too. They operate natively on fp16 inputs only; CUDA cores handle fp32.
- The speed comes from one Tensor Core doing a 4×4 matmul in a single cycle vs many cycles on CUDA cores.

## Verdict

Close enough on the big picture. Kept current interval.

**Next review:** ~2026-07-08
