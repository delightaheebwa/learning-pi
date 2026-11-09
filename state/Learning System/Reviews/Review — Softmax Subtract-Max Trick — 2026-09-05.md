# REVIEW: Softmax Subtract-Max Trick — 2026-09-05

## Review Info

- **Date:** [[2026-09-05]]
- **Concept:** Softmax Subtract-Max Trick
- **Last Reviewed:** 2026-09-01
- **Review Interval:** 4 days
- **Status Before Review:** developing
- **Q Type:** discriminative (Last Q Type was definitional)

---

## Assistant's Prompt

> *"softmax([3,1,0]) vs softmax([-0,-2,-3]) (max-subtracted) — same or different, and what does naive `exp` do on [1000,1001,1002] in float32? One line."*

---

## Your Answer

- **Confidence before evaluation:** confident
- **Answer:** Same. Naive exp overflows each value to infinity.

---

## Assistant's Evaluation

- **Result:** Pass
- **Feedback:** Both halves right. Shift-invariance (subtracting a constant cancels in numerator/denominator) plus the overflow mechanic: exp(1000) ≈ 1e434 ≫ float32 max 3.4e38 → inf. That is exactly why the trick exists.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing (unchanged)
- **last_reviewed:** 2026-09-05
- **next_review:** 2026-09-12 (procedure pass: interval_index 0→1, +7d)
- **Last Q Type:** discriminative
- **notes:** Shift-invariance + overflow rationale both solid.

---

## Queue / Deferred Note

- **Queue position:** active

---

## Key Takeaway

> Subtract-max is free (identical output) and saves softmax from drowning in inf.
