# REVIEW: Automatic differentiation — 2026-05-07

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** 2026-05-07
- **Concept:** Automatic differentiation
- **Last Reviewed:** 2026-05-05
- **Review Interval:** 2 days
- **Status Before Review:** developing

---

## Zo's Prompt

> Zo will ask you a question or give you a scenario. Record it here.

> _"Zo asked: In your own words, what is automatic differentiation, and how is forward mode different from reverse mode?"_

---

## Your Answer

> Your response — try to answer from memory before reading any notes.

- **Confidence before evaluation:** 6/10
- **Answer:**
  - Automatic differentiation refers to differentiation where expressions are broken down into their primitive operations and those operations are differentiated.
  - Forward mode gets intermediate variables and their derivatives left to right in one pass.
  - Reverse mode first does a forward pass to get the intermediate variables and then a backward pass to get their derivatives.

---

## Zo's Evaluation

- **Result:** Pass
- **Feedback:** Mostly right. The main nuance is that automatic differentiation applies the chain rule through a computation graph, forward mode carries derivatives alongside values left to right, and reverse mode is especially efficient for gradients of a scalar loss.
- **Status After Review:** pending_mastery

---

## Updated Concept Record

- **status:** updated
- **last_reviewed:** 2026-05-07
- **next_review:** 2026-05-11
- **review_interval:** 4 days
- **notes:** Good retrieval with one correction on reverse-mode efficiency; review passed and concept moved to pending_mastery.

---

## Queue / Deferred Note

- **Queue position:** active
- **If deferred:** 

---

## Key Takeaway

> Automatic differentiation is the chain rule applied through a computation graph, and reverse mode is the workhorse for scalar-loss gradient backpropagation.
