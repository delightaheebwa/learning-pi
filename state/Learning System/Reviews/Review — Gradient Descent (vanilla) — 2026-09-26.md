# Review — Gradient Descent (vanilla) — 2026-09-26

- **Track/Source:** aiefs — Rohit P1 L08 + handwritten notes 2026-09-08 (Python)
- **Type:** procedure · **Q type:** discriminative (MCQ)
- **Why this slot:** due review (row was overdue since 2026-09-24); the learning-rate symptom check for the plain update, kept distinct from the zigzag/overshoot conflation tracked separately (and not asked adjacent to it).
- **Question:** For vanilla GD w ← w − η∇w, which symptom matches η too LARGE?
- **Learner answer:** B — steps overshoot the minimum; the loss bounces or even blows up.
- **Verdict:** PASS — grade-audit agreed. Distractors dodged: A is the too-small crawl, C is grad = 0 (not an lr symptom), D describes adaptive methods (Adam).
- **Attempts.json:** mastery 1.00, interval_index 2, next_review 2026-10-10, Feynman: —
- **Mistakes ledger:** no mistake row for this concept (the open application row belongs to Zigzag vs Overshoot, not vanilla); clean pass, nothing to graduate.
- **Calibration:** the too-large / too-small / zero-gradient / adaptive-methods four-way split is retrieval-solid; the 2026-10-10 probe can raise the bar to the functional form of one step.
