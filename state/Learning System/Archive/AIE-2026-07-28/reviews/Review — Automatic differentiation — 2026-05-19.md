# REVIEW: Automatic Differentiation — 2026-05-19

## Review Info

- **Date:** 2026-05-19
- **Concept:** Automatic differentiation
- **Last Reviewed:** 2026-05-07
- **Review Interval:** 12 days
- **Status Before Review:** pending_mastery

---

## Zo's Prompt

*Zo asked: "Explain how automatic differentiation works — what's the core idea, and how do forward mode and reverse mode differ? Walk me through both."*

---

## Your Answer

- **Confidence before evaluation:** confident
- **Answer:** Automatic differentiation breaks complex expressions into primitives and differentiates those primitives. Forward mode computes derivatives left-to-right alongside values. Reverse mode stores intermediate values on the forward pass, then computes derivatives right-to-left on the backward pass.

---

## Zo's Evaluation

- **Result:** Pass
- **Feedback:** Core understanding solid. Sharpened on chain rule being the underlying mechanism, JVP vs VJP terminology, and the efficiency argument (reverse mode for many-inputs-few-outputs, forward mode for few-inputs-many-outputs).
- **Status After Review:** mastered

---

## Updated Concept Record

- **status:** mastered
- **last_reviewed:** 2026-05-19
- **next_review:** 2026-05-26
- **review_interval:** 7 days
- **notes:** Solid recall of forward vs reverse mode, JVP/VJP distinction, and efficiency rationale for neural networks.

---

## Queue / Deferred Note

- **Queue position:** not queued
- **If deferred:** —

---

## Key Takeaway

AD is chain rule on a computational graph; forward mode computes JVPs left-to-right, reverse mode computes VJPs right-to-left, and reverse mode wins for neural nets because cost scales with outputs, not parameters.
