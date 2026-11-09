# REVIEW: Automatic differentiation — 2026-06-03

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** 2026-06-03
- **Concept:** Automatic differentiation
- **Last Reviewed:** 2026-05-18
- **Review Interval:** 16 days
- **Status Before Review:** developing

---

## Zo's Prompt

> Zo will ask you a question or give you a scenario. Record it here.

> _"Imagine a neural network with millions of parameters and a single scalar loss. Explain why reverse-mode AD is the natural fit, and describe the forward pass and backward pass at a high level."_

---

## Your Answer

> Your response — try to answer from memory before reading any notes.

- **Confidence before evaluation:** not yet reviewed
- **Answer:**
-

---

## Zo's Evaluation

- **Result:** Pending
- **Feedback:** Not reviewed yet.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing
- **last_reviewed:** 2026-05-18
- **next_review:** 2026-06-03
- **review_interval:** 16 days
- **notes:** Reverse mode is efficient for many inputs and one output because gradients for all inputs can be accumulated from one backward sweep after storing the needed intermediates from the forward pass.

---

## Queue / Deferred Note

- **Queue position:** scheduled
- **If deferred:** Future review placeholder.

---

## Key Takeaway

> Reverse-mode AD is what makes gradient-based training practical for large neural networks.
