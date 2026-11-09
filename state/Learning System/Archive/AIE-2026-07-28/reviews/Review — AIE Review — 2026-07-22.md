# Review — AIE Review — 2026-07-22

**Date:** 2026-07-22
**Track:** AI Engineering (aie)
**Session:** 5 concepts reviewed

## Concepts

### Two-Pass Autodiff Algorithm ✅ → 14d
**Q:** What makes reverse-mode efficient for NNs with millions of params vs forward-mode?
**A:** One backward pass gives gradients for all parameters; forward-mode needs a pass per parameter.

### Computational Graphs (Autodiff) ⚠️ → keep 3d
**Q:** Why break into a graph of primitives instead of symbolic derivative?
**A:** Correct insight (symbolic derivative expression swell). Sharpened: symbolic diff causes exponential expression growth; autodiff evaluates numeric derivatives along primitives combined via chain rule without expanding.

### Local Autograd Derivative Rules ❌ (term recall) → keep 3d
**Q:** Why `+=` instead of `=` in `_backward`?
**User:** "Weights won't update / learning stalls"
**Correction:** Fan-out — a node feeding multiple downstream ops needs `+=` to sum all gradient contributions. `=` silently drops all but the last path. The canonical example is `a + a`.

### Gradient Accumulation (+=) ⚠️ → keep 3d
**Q:** Why zero `.grad = 0` before each step instead of overwriting?
**A:** Correct consequence (old gradients distort direction). Sharpened: without zeroing, `.grad` accumulates across training steps, not just fan-out — you get a blend of gradients from multiple steps, no longer the gradient of the current loss.

### Topological Sort for Backprop ⚠️ → keep 7d
**Q:** Why topological ordering, and what breaks with reverse input order?
**A:** Correct intuition. Sharpened: reverse topo guarantees every grad contribution from all downstream paths is in before propagating. Reverse input order could process a leaf before a dependent node that fans into it has run.
