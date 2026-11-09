# Review — Print Debugging & breakpoint for AI

**Date:** 2026-07-02
**Track:** AI Engineering (aie)
**Concept:** Print Debugging & breakpoint for AI
**Source:** ai-engineering-from-scratch Phase 0, Lesson 12

## Performance

**Retrieval attempt:** Knew conditional breakpoint triggered on NaN detection. Understood `pdb` for inspection. Said "pdb outputs.shape" instead of "p outputs.shape".

### Correct pattern:
```python
if torch.isnan(loss) or torch.isinf(loss):
    breakpoint()
```
Inside pdb: `p outputs.shape`, `p outputs.isnan().sum()`, `p outputs.min()`, `p outputs.max()`, `p model.layer.weight.grad`

**Verdict:** ⚠️ Kept current interval
**Next review:** 2026-07-05
