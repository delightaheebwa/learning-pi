# REVIEW: PMF vs PDF — 2026-09-05

## Review Info

- **Date:** [[2026-09-05]]
- **Concept:** PMF vs PDF
- **Last Reviewed:** 2026-09-01
- **Review Interval:** 4 days
- **Status Before Review:** developing
- **Q Type:** discriminative (Last Q Type was definitional)

---

## Assistant's Prompt

> *"A fair die shows P(X=3)=1/6, but a height model gives f(170cm)=2.0 — which one is PMF vs PDF, and why can't 2.0 be a probability as-is? One line, own words."*

---

## Your Answer

- **Confidence before evaluation:** confident
- **Answer:** Die = PMF, height = PDF. A probability must live in [0,1], so 2.0 can't be one.

---

## Assistant's Evaluation

- **Result:** Pass
- **Feedback:** Correct on both halves. Shelf-ready addendum: 2.0 is legal as a *density* — only the *area* under it over an interval must land in [0,1]. Tall-narrow curves can exceed 1 and still integrate to 1.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing (unchanged)
- **last_reviewed:** 2026-09-05
- **next_review:** 2026-09-12 (concept pass: interval_index 0→1, +7d)
- **Last Q Type:** discriminative
- **notes:** 0–1 bound solid; density-vs-probability distinction reinforced (integrate, don't point-read).

---

## Queue / Deferred Note

- **Queue position:** active

---

## Key Takeaway

> PMF answers "probability of this exact value"; PDF answers "density here — integrate me for probability."
