# Review — Chain Rule & Backpropagation — 2026-07-10

**Concept:** Chain Rule & Backpropagation  
**Date:** 2026-07-10  
**Result:** Advanced (3d → 7d)

**Question:** Why does backpropagation need the chain rule? One sentence.

**Response:** Neural networks are stacked/composed functions, and the chain rule lets you propagate gradients through that composition to tune the weights.

**Evaluation:** Fully correct. "Stacked functions" framing is spot-on — the chain rule is the mechanism that decomposes the gradient of a composition into local steps.

**New Interval:** 7d — next review 2026-07-17
