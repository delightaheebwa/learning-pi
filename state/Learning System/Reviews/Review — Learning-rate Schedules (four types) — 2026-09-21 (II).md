# REVIEW: Learning-rate Schedules (four types) — 2026-09-21 (II)

## Review Info

- **Date:** [[2026-09-21]] (second review session of the day)
- **Concept:** Learning-rate Schedules (four types)
- **Slot:** 1 — due mistake (oldest; 09-10 rows next 09-13/09-17, floor-value slip)
- **Status Before Review:** developing · Last Q Type discriminative
- **Q Type:** discriminative (fresh paraphrased curves)

---

## Assistant's Prompt

> *"Curve A: starts 0.01, ramps to 0.1 over the first 10% of training, then decays smoothly, flattening at exactly 0.05. Curve B: decays by a constant factor toward 0. Curve C: half-cosine arc down to exactly 0.05. Which schedule is Curve A, and what is its eta_min?"*

---

## Your Answer

- **Answer:** warmup. floor value = 0.05

---

## Assistant's Evaluation

- **Result:** Pass (grade-audit agreed)
- **Feedback:** Both halves land. Warmup is the only schedule that ramps up at the start; the floor value came back exact (η_min = 0.05) — the half that slipped on 09-17 ("very small positive number"). Trio now clean: warmup = ramp-up, cosine = nonzero floor, exponential = no floor.
- **Attempt:** pass — mastery 0.75, interval_index 3, next_review 2026-10-21.
- **Mistakes rows:** all three LR rows bump one consecutive correct (09-19 row graduates; 09-10/09-17 rows → review, due 2026-10-21).
