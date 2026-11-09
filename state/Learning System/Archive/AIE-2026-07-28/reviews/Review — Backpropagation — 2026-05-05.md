# REVIEW: Backpropagation — 2026-05-05

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** 2026-05-05
- **Concept:** Backpropagation
- **Last Reviewed:** 2026-05-02
- **Review Interval:** 3 days
- **Status Before Review:** developing

---

## Zo's Prompt

> Zo will ask you a question or give you a scenario. Record it here.

> _"From memory, explain backpropagation by describing the forward pass and the backward pass, and say why the backward pass is efficient."_

---

## Your Answer

> Your response — try to answer from memory before reading any notes.

- **Confidence before evaluation:** 3/5
- **Answer:** During the forward pass, backpropagation computes and stores the intermediate activations. During the backward pass, it uses those stored values to compute derivatives and gradients for the loss and earlier layers.

---

## Zo's Evaluation

- **Result:** Pass
- **Feedback:** Good start. The key refinement was that the backward pass uses the chain rule to propagate gradients from the loss through each layer, and the forward-pass values are stored so those local derivatives can be reused efficiently.
- **Status After Review:** pending_mastery

---

## Updated Concept Record

- **status:** updated
- **last_reviewed:** 2026-05-05
- **next_review:** 2026-05-12
- **review_interval:** 7 days
- **notes:** Forward pass stores activations/intermediates; backward pass reuses them and applies the chain rule from the loss backward to compute parameter gradients and earlier-layer gradients.

---

## Queue / Deferred Note

- **Queue position:** active
- **If deferred:** N/A

---

## Key Takeaway

> Backpropagation reuses stored forward-pass values to send gradients backward efficiently.
