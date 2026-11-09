# REVIEW: Cosine Similarity — 2026-09-05

## Review Info

- **Date:** [[2026-09-05]]
- **Concept:** Cosine Similarity
- **Last Reviewed:** 2026-09-01
- **Review Interval:** 4 days
- **Status Before Review:** developing
- **Q Type:** discriminative (Last Q Type was definitional)

---

## Assistant's Prompt

> *"Doc embeddings A=[1,0], B=[0,1], C=[2,0] — what is cos(A,B) vs cos(A,C), and why does that pair prove cosine ignores magnitude where raw dot product doesn't? One line, no paper."*

---

## Your Answer

- **Confidence before evaluation:** uncertain
- **Answer:** cos(A,B) = 90 degrees, cos(A,C) = 0 degrees; dot product tells the better story of similarity.

---

## Assistant's Evaluation

- **Result:** Needs More Work
- **Feedback:** Right picture, wrong labels, inverted moral. (1) Asked for *cosines*, got *angles*: cos(A,B)=0, cos(A,C)=1. (2) C=2A points the same way as A, so cosine says identical (1) — magnitude washed out by unit-norm division. Raw dot *conflates* magnitude with similarity: dot(A,C)=2 vs dot(A,A)=1 for the same direction. Dot tells a *worse* story here, not a better one — that inversion is the thing to fix.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing (unchanged)
- **last_reviewed:** 2026-09-05
- **next_review:** 2026-09-08 (fail: interval_index reset, +3d)
- **Last Q Type:** discriminative
- **notes:** Mistake row added (structural, active, retry 2026-09-08). Drill cue: "same direction, different length → cosine 1, dot differs."

---

## Queue / Deferred Note

- **Queue position:** active — priority-1 mistake retry due 2026-09-08

---

## Key Takeaway

> Cosine answers "same direction?" (C=2A scores 1); dot smuggles length into the answer.
