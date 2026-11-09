# REVIEW: Gradient Descent Failure Modes (zigzag vs overshoot) — 2026-09-21 (II)

## Review Info

- **Date:** [[2026-09-21]] (second review session of the day)
- **Concept:** Gradient Descent Failure Modes (zigzag vs overshoot)
- **Slot:** 2 — due mistake (2026-09-07 row, status review, next 09-19)
- **Q Type:** discriminative

---

## Assistant's Prompt

> *"Vanilla GD is descending the Rosenbrock valley. You lower the learning rate substantially — the violent overshooting stops, but the path still crawls: big oscillations side-to-side across the valley, tiny progress along its length. Which failure mode is still present, and what does lowering η actually fix? (One line.)"*

---

## Your Answer

- **Answer:** "the failure mode is that vanilla gd doesnt consider how big the step size should be based on the gradient hence it ends moving slowly and having big oscialltions. lowering n just makes the steps small but not adaptive."

---

## Assistant's Evaluation

- **Result:** Fail (grade-audit agreed)
- **Feedback:** The 09-07 conflation recurred. The oscillation was attributed to step-size handling ("doesn't consider how big the step should be", "not adaptive") — the overshoot story. But overshoot is exactly what lowering η fixed. What persists is zigzag: in a narrow valley the gradient itself points mostly ACROSS the walls, not along the valley — a direction problem, not a step-size problem. Lowering η shrinks the zigzag but can't straighten it.
- **Attempt:** fail — mastery 0.38, interval_index 0, next_review 2026-09-24.
- **Deep-dive (learner requested):** why GD points across walls — the gradient is perpendicular to the local contours; a narrow valley packs contours tightly across the walls and spreads them along the floor, so the locally-steepest step aims at the nearest wall. The gradient only knows local slope, so plain GD has no memory to average the cross-valley flips; momentum cancels the alternating cross-valley component and accumulates the consistent along-valley one (fact-check PASS on all four claims).
- **State:** Mistakes row stays open (active, next 09-24). NOTE: this concept had no Active Concepts row (Attempts/Mistakes tracked it only) — a row was added today to close that drift.
