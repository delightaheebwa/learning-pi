# Review — Numerical vs Analytical Derivatives — 2026-07-10

**Concept:** Numerical vs Analytical Derivatives  
**Date:** 2026-07-10  
**Result:** Advanced (3d → 7d)

**Question:** What's the key tradeoff between analytical and numerical derivatives?

**Response:** Numerical works for any function but produces an approximation and is slower; analytical is fast and exact but may not apply to all functions.

**Evaluation:** Mostly correct. The "may not apply" framing is slightly off — analytical derivatives work on any differentiable function, but someone has to manually derive the formula. The real tradeoff: numerical = automatic but approximate, analytical = exact but manual. Autodiff (PyTorch's approach) bridges this — exact like analytical, automatic like numerical.

**New Interval:** 7d — next review 2026-07-17
