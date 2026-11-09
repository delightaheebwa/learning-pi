# REVIEW: Jacobian-vector product — 2026-05-08

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** 2026-05-08
- **Concept:** Jacobian-vector product
- **Last Reviewed:** 2026-05-05
- **Review Interval:** 3 days
- **Status Before Review:** developing

---

## Zo's Prompt

> Zo asked: What does `J_f(x)r` mean, and how is it connected to the directional derivative you just gave?

---

## Your Answer

> Your response — try to answer from memory before reading any notes.

- **Confidence before evaluation:** confident
- **Answer:**
  - "It means the product of the Jacobian of f(x) and the vector r. It shows the effect of a tiny change at a point in the direction of the vector r hence it is a directional derivative."

---

## Zo's Evaluation

- **Result:** Pass
- **Feedback:** Correct. `J_f(x)r` means applying the Jacobian to a vector, and when that vector is a unit direction vector it matches the directional derivative. More generally, forward-mode AD computes this efficiently without materializing the full Jacobian.
- **Status After Review:** pending_mastery

---

## Updated Concept Record

- **status:** pending_mastery
- **last_reviewed:** 2026-05-08
- **next_review:** 2026-05-15
- **review_interval:** 7 days
- **notes:** Remember that a JVP is Jacobian times a vector, and it matches a directional derivative for a unit direction vector.

---

## Queue / Deferred Note

- **Queue position:** active
- **If deferred:** N/A

---

## Key Takeaway

> A Jacobian-vector product is the Jacobian applied to a vector; it becomes a directional derivative for a unit direction vector.
