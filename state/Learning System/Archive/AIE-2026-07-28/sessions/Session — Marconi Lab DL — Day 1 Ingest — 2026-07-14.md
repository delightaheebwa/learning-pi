# Session — Marconi Lab DL — Day 1 Ingest

- **Date:** 2026-07-14
- **Topic:** Marconi Lab Deep Learning — Day 1: Tensors, Neural Networks & the Training Loop
- **Source:** Marconi Lab DL Course, Day 1 (HTML lesson)
- **Type:** Ingest

## Concepts Ingested

| Concept | Status | Next Review | Wiki |
|---|---|---|---|
| Tensors (PyTorch) | developing | 2026-07-17 | [[Tensors (PyTorch)]] |
| PyTorch Model Building | developing | 2026-07-18 | [[PyTorch Model Building]] |
| Activation Functions | developing | 2026-07-19 | [[Activation Functions]] |
| Loss Functions (PyTorch) | developing | 2026-07-17 | [[Loss Functions (PyTorch)]] |
| Training Loop Pattern | developing | 2026-07-18 | [[Training Loop Pattern]] |
| Evaluation Protocol | developing | 2026-07-19 | [[Evaluation Protocol]] |

## Summary

Ingested the Marconi Lab DL Day 1 lesson covering the foundational training loop pattern. Key takeaways:

- Tensors are the universal data container in DL — all data types (images, text, audio, tabular) become tensors with a [batch, channels, H, W] or [batch, features] shape convention
- Every PyTorch model subclasses nn.Module, defining layers in __init__ and data flow in forward()
- The 5-step training loop mantra: Zero → Forward → Loss → Backward → Update — identical across every model
- Cross-entropy expects raw logits (no softmax in forward)
- eval() + no_grad() essential for correct evaluation
