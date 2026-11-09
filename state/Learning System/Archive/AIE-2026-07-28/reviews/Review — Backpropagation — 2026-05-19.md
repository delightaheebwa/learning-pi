# REVIEW: Backpropagation — 2026-05-19

## Review Info

- **Date:** 2026-05-19
- **Concept:** Backpropagation
- **Last Reviewed:** 2026-05-05
- **Review Interval:** 14 days
- **Status Before Review:** pending_mastery

---

## Zo's Prompt

*Zo asked: "Walk me through backpropagation for a simple two-layer neural network. What gets computed in the forward pass, what gets computed in the backward pass, and what chain of derivatives connects the loss to W₁?"*

---

## Your Answer

- **Confidence before evaluation:** uncertain
- **Answer:** Described forward/backward passes at a high level, then attempted a chain of partial derivatives but got the chain wrong (suggested ∂W₂/∂W₁ instead of flowing through activations).

---

## Zo's Evaluation

- **Result:** Needs More Work
- **Feedback:** High-level summary was correct but couldn't trace the specific chain: ∂L/∂W₁ = ∂L/∂ŷ · ∂ŷ/∂z₂ · ∂z₂/∂h · ∂h/∂z₁ · ∂z₁/∂W₁. The key mistake was thinking weights depend on each other — they don't; the chain flows through activations. ReLU mask and outer product for weight gradients were missing.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing
- **last_reviewed:** 2026-05-19
- **next_review:** 2026-05-22
- **review_interval:** 3 days (reset)
- **notes:** Can describe the two-pass structure but cannot trace a specific gradient chain through a two-layer network. Needs practice with concrete examples.

---

## Queue / Deferred Note

- **Queue position:** not queued
- **If deferred:** —

---

## Key Takeaway

Backprop chains flow through activations, not weights — W₁ and W₂ are independent parameters, and the chain rule flows from loss → output → hidden → input.
