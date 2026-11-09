# Session — Makemore Part 2 & Regularization — 2026-07-22

**Date:** 2026-07-22
**Track:** aie
**Source material:** `02-makemore-bigram.html` (Part 2) + Gemini tutoring session on regularization & hidden layers

## Concepts Ingested

| Concept | Status | Next Review | Source |
|---------|--------|-------------|--------|
| One-Hot Encoding | developing | 2026-07-25 | makemore Part 2 |
| Softmax Function | developing | 2026-07-25 | makemore Part 2 |
| Row-Select Property | developing | 2026-07-25 | makemore Part 2 |
| L2 Regularization as Smoothing | developing | 2026-07-28 | makemore Part 2 + Gemini session |
| Regularization Tug-of-War | developing | 2026-07-28 | Gemini session |
| Distributed Representations (Character Embeddings) | developing | 2026-07-30 | Gemini session |
| Hidden Layers Generalize via Shared Weights | developing | 2026-07-30 | Gemini session |

**From supplementary discrete-vs-continuous material:** Deepened the Distributed Representations concept with a clear explanation of why continuous (floating-point) embeddings matter — they enable gradient flow and distance measurement between characters, which discrete one-hot buckets cannot do.

## Open Questions

- How does the row-select property extend to embedding layers in larger models? (nn.Embedding vs one-hot @ W)
- What's the relationship between L2 regularization and dropout in terms of distribution smoothing?

## Notes

- The unstructured naming was wrong — the file was already named with its actual content. The "Semantic Scolars" attempt was a Gemini hallucination I didn't catch. Corrected to the Gemini tutoring session description.
- Key insight from Part 2: the neural bigram is identical to the counting approach — one-hot @ W = row selection. The framework generalization (to MLPs, RNNs, transformers) is what makes the neural version powerful.
- Regularization tug-of-war is a mental model worth returning to: every regularization technique is a second team pulling against the data loss.
