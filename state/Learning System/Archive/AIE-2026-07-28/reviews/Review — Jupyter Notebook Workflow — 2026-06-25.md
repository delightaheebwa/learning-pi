# Review — Jupyter Notebook Workflow

**Date:** 2026-06-25
**Concept:** Jupyter Notebook Workflow
**Status:** Developing (kept interval)

## Retrieval Performance

**Question:** What's the cell-kernel architecture in Jupyter, and what's the "hidden state" trap? Why is that trap especially dangerous in AI/ML work?

**Result:** Close — correctly described the cell-kernel architecture and the hidden state trap (variables from deleted cells persist, execution order matters). Missed the AI/ML-specific danger.

## Correction

Hidden state is especially dangerous in AI/ML because ML workflows are iterative and long-running — out-of-order execution can silently overwrite a model weight, batch size, or data split, wasting hours of training before you notice.

## Next Review: 2026-06-28
