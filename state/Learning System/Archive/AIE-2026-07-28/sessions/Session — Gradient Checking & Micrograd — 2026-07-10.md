# Session — Chain Rule & Autodiff: Lesson 5 Ingest

**Date:** 2026-07-10
**Topic:** Gradient Checking & Micrograd in Action
**Source:** `teach/lessons/0005-gradient-checking-and-micrograd.html`

## Concepts Ingested

| # | Concept | Wiki | Next Review |
|---|---------|------|-------------|
| 1 | Gradient Checking | [[Gradient Checking]] | 2026-07-13 |
| 2 | Neural Network Training Loop | [[Neural Network Training Loop]] | 2026-07-13 |
| 3 | Micrograd Architecture | [[Micrograd Architecture]] | 2026-07-13 |

## Summary

Lesson 5 completes the Chain Rule & Autodiff mission. Key takeaways:

- **Gradient checking** uses central finite differences to numerically verify autograd correctness. Should be done after implementing any new operation.
- **The training loop** ties everything together: forward pass → loss → loss.backward() → update params → zero gradients → repeat.
- **Micrograd architecture**: 5-level hierarchy from Value scalar → Neuron → Layer → MLP → Training Loop. This is what PyTorch does, just with tensors and GPUs.

## Status

- AI Engineering (aie): 60 developing (was 57)
- All 3 concepts on 3-day interval, first review 2026-07-13
