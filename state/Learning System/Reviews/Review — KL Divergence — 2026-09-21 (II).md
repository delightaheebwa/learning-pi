# REVIEW: KL Divergence — 2026-09-21 (II)

## Review Info

- **Date:** [[2026-09-21]] (second review session of the day)
- **Concept:** KL Divergence
- **Slot:** 5 — due mistake (2026-09-18 row: per-term sign read as a "negative relationship" — corrected same session, never re-tested)
- **Q Type:** discriminative (Last Q Type was definitional)

---

## Assistant's Prompt

> *"For Q = (0.5, 0.5) and P = (0.8, 0.2), look at the first term of D_KL(Q ∥ P) = Σᵢ qᵢ log₂(qᵢ/pᵢ). What is the sign of the first term 0.5·log₂(0.5/0.8), and what does that sign mean — rebate or cost?"*

---

## Your Answer

- **Answer:** it is negative. this is a per-outcome rebate

---

## Assistant's Evaluation

- **Result:** Pass (grade-audit agreed)
- **Feedback:** Correct on fresh numbers: Q₁ = 0.5 < P₁ = 0.8, so log₂(0.5/0.8) < 0 — the model overestimates that outcome, its code is shorter than the truth-optimal one: a rebate. The 09-18 category slip (per-term sign ≠ correlation sign between variables) now holds under retrieval — one consecutive correct.
- **Attempt:** pass — mastery 1.00, interval_index 3, next_review 2026-10-21.
- **Mistakes row:** one consecutive correct → review, due 2026-10-21.
