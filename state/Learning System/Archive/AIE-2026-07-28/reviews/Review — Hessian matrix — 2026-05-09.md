# REVIEW: Hessian matrix — 2026-05-09

> **Purpose:** When a concept comes up for spaced repetition review, use this note to capture the review session. Zo will test you on the concept and the results update the Knowledge Base.

## Review Info

- **Date:** 2026-05-09
- **Concept:** Hessian matrix
- **Last Reviewed:** 2026-05-06
- **Review Interval:** 3 days
- **Status Before Review:** developing

---

## Zo's Prompt

> Zo will ask you a question or give you a scenario. Record it here.

> _"From memory, explain what the Hessian matrix is, when it is symmetric, and what it tells you about curvature around a point."_

---

## Your Answer

> Your response — try to answer from memory before reading any notes.

- **Confidence before evaluation:** uncertain
- **Answer:**
  - The Hessian matrix is the collection of all second-order partial derivatives of a scalar function.
  - For a function of two variables, the full Hessian is:

```latex
H(f)=
\begin{pmatrix}
\frac{\partial^2 f}{\partial x^2} & \frac{\partial^2 f}{\partial x \partial y} \\
\frac{\partial^2 f}{\partial y \partial x} & \frac{\partial^2 f}{\partial y^2}
\end{pmatrix}
```

  - The off-diagonal terms are mixed partial derivatives.
  - For smooth functions, the Hessian is symmetric when the mixed partials are continuous.

---

## Zo's Evaluation

- **Result:** Pass
- **Feedback:** Good. You correctly wrote the full 2×2 Hessian and correctly identified the off-diagonal entries as mixed partial derivatives. You also recalled that smooth functions give a symmetric Hessian when the mixed partials are continuous.
- **Status After Review:** pending_mastery

---

## Updated Concept Record

- **status:** pending_mastery
- **last_reviewed:** 2026-05-09
- **next_review:** 2026-05-16
- **review_interval:** 7 days
- **notes:** Matrix of second-order partial derivatives; symmetric when mixed partials are continuous; curvature information around a point; off-diagonal entries are mixed partial derivatives.

---

## Queue / Deferred Note

- **Queue position:** not queued
- **If deferred:** Scheduled future review placeholder.

---

## Key Takeaway

> The Hessian packages second-order curvature information into a matrix, with mixed partials on the off-diagonal.
