# Review — Learning-rate Schedules (four types) — 2026-09-19

- **Q (definitional, quiz-audit PASS):** Define the eta-vs-t curve shape of warmup / step decay / exponential decay / cosine annealing, one phrase each.
- **A:** warmup ramps up quickly then decays; step = flat-drop-flat staircase; exponential decays toward zero, no floor; cosine ramps up and decays, stops at a floor.
- **Grade: FAIL (grade-audit agreed).** Step / exponential / warmup-ramp correct; cosine given a ramp-up — only warmup ramps (early-phase discriminator re-inverted; recurrence of the 09-10 cosine-vs-warmup confusion).
- **Repair:** early phase = warmup ramps, everything else starts high; end behavior = only cosine stops at a nonzero floor eta_min.
- **State:** Attempts fail → mastery 0.15, interval_index 0, next_review 2026-09-22. New Mistakes row (active, 2026-09-19).
