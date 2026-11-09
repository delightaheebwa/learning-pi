# REVIEW: Automatic differentiation — 2026-05-18

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** 2026-05-18
- **Concept:** Automatic differentiation
- **Last Reviewed:** 2026-05-11
- **Review Interval:** 7 days
- **Status Before Review:** developing

---

## Zo's Prompt

> Zo will ask you a question or give you a scenario. Record it here.

> _"Explain forward-mode AD and reverse-mode AD in your own words, and tell me which one is better when there are few inputs and many outputs versus many inputs and one output."_

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
- **last_reviewed:** 2026-05-11
- **next_review:** 2026-05-18
- **review_interval:** 7 days
- **notes:** Forward mode pairs each primal with a tangent and is efficient for few inputs/many outputs; reverse mode stores intermediates on the forward pass and propagates adjoints backward, which is ideal for many inputs/few outputs.

---

## Queue / Deferred Note

- **Queue position:** scheduled
- **If deferred:** Future review placeholder.

---

## Key Takeaway

> The right AD mode depends on whether the function is input-heavy or output-heavy.
