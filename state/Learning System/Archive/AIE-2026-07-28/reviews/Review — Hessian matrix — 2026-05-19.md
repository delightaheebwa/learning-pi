# REVIEW: Hessian Matrix — 2026-05-19

## Review Info

- **Date:** 2026-05-19
- **Concept:** Hessian matrix
- **Last Reviewed:** 2026-05-09
- **Review Interval:** 10 days
- **Status Before Review:** pending_mastery

---

## Zo's Prompt

*Zo asked: "What is the Hessian matrix?" then "In optimization, what specific information does the Hessian give you that lets optimizers like Newton's method converge faster than gradient descent?"*

---

## Your Answer

- **Confidence before evaluation:** uncertain
- **Answer:** Correctly defined the Hessian as a matrix of second-order partial gradients describing local curvature. On the optimization question, described curvature-sensitive step sizing but missed the quadratic approximation and direct-solve mechanism.

---

## Zo's Evaluation

- **Result:** Needs More Work
- **Feedback:** The definition was solid. But the optimization advantage isn't just step sizing — Newton's method uses the Hessian to build a local quadratic approximation and then solves for its minimum directly: Δx = -H⁻¹∇f(x). This gives quadratic convergence near the optimum, not just better step sizes.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing
- **last_reviewed:** 2026-05-19
- **next_review:** 2026-05-22
- **review_interval:** 3 days (reset)
- **notes:** Knows the definition but hasn't connected the Hessian to Newton's method's quadratic approximation and direct-solve update.

---

## Queue / Deferred Note

- **Queue position:** not queued
- **If deferred:** —

---

## Key Takeaway

The Hessian enables a local quadratic approximation; Newton's method solves for its minimum directly, giving quadratic convergence — faster than gradient descent's linear convergence.
