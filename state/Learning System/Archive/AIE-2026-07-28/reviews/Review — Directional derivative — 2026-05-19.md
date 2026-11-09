# REVIEW: Directional Derivative — 2026-05-19

## Review Info

- **Date:** 2026-05-19
- **Concept:** Directional derivative
- **Last Reviewed:** 2026-05-08
- **Review Interval:** 11 days
- **Status Before Review:** developing

---

## Zo's Prompt

*Zo asked: "What is the directional derivative, and how is it computed? Give me the formula and explain what each part means."*

---

## Your Answer

- **Confidence before evaluation:** uncertain
- **Answer:** "Intuitively, directional derivative refers to the effect of a tiny change on a variable in a certain direction. The formula is derivative × JVP."

---

## Zo's Evaluation

- **Result:** Needs More Work
- **Feedback:** Intuition is on track but the formula was off. The correct formula is D_v f(x) = ∇f(x) · v (gradient dot direction vector). The connection to JVP is real (J_f(x) · v = ∇f · v for scalar functions), but the formula is dot product, not "derivative × JVP."
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing
- **last_reviewed:** 2026-05-19
- **next_review:** 2026-05-22
- **review_interval:** 3 days (reset)
- **notes:** Needs to internalize the exact formula: D_v f(x) = ∇f(x) · v. Each gradient component gives rate of change along its axis; the dot product combines them for direction v.

---

## Queue / Deferred Note

- **Queue position:** not queued
- **If deferred:** —

---

## Key Takeaway

The directional derivative is the dot product of the gradient and the direction vector — not a product of two separate derivative quantities.
