# REVIEW: Chain Rule for Neural Networks — 2026-09-05

## Review Info

- **Date:** [[2026-09-05]]
- **Concept:** Chain Rule for Neural Networks
- **Last Reviewed:** 2026-09-01
- **Review Interval:** 4 days
- **Status Before Review:** developing
- **Q Type:** discriminative (Last Q Type was definitional)

---

## Assistant's Prompt

> *"y = 3x+2, z = y², L = ln(z) at x=1. Compute dL/dx via the chain product (dL/dz)·(dz/dy)·(dy/dx). What do you get — and would adding the three terms even come close? Work on paper, reply with just the final number."*

---

## Your Answer

- **Confidence before evaluation:** confident
- **Answer:** 1.2. Guessed the sum "kinda comes close" at 0.52.

---

## Assistant's Evaluation

- **Result:** Pass
- **Feedback:** 1.2 is exactly right (dL/dz=1/25=0.04, dz/dy=10, dy/dx=3 → 0.04·10·3). But the sum guess was off twice over: the true sum is 0.04+10+3=13.04, not 0.52 (recheck the middle term on paper) — and 13.04 vs 1.2 is not close at all. That gap IS the lesson: dependent links multiply, never add.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing (unchanged)
- **last_reviewed:** 2026-09-05
- **next_review:** 2026-09-12 (procedure pass: interval_index 0→1, +7d)
- **Last Q Type:** discriminative
- **notes:** Chain product solid; addition-sum arithmetic wobbled — recompute term-by-term on paper next time.

---

## Queue / Deferred Note

- **Queue position:** active

---

## Key Takeaway

> Gradients across dependent layers multiply (1.2), and the additive guess (13.04) isn't even in the same postcode.
