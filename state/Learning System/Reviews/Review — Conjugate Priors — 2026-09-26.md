# Review — Conjugate Priors — 2026-09-26

- **Track/Source:** aiefs — Rohit P1 L07 + Think Bayes (Python)
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** due review and retry of the 2026-09-19 slip on the Beta-Binomial update rule.
- **Question:** Prior Beta(2,2), coin flipped 3 times, all heads — what do you do to get the posterior? A) add yesterday's posterior to today's prior Beta(2+2,2+2); B) add observed counts to the prior's parameters Beta(2+3,2+0); C) tail count to the first parameter / head to the second Beta(2+0,2+3); D) add the total flip count to each parameter Beta(2+3,2+3).
- **Learner answer:** D — add the total flip count to each parameter Beta(2+3,2+3).
- **Verdict:** FAIL — grade-audit agreed. Correct: B — 3 successes go to the first parameter (a+3), 0 failures to the second (b+0) → Beta(5,2); D discards WHICH outcomes occurred.
- **Attempts.json:** mastery 0.19, interval_index 0, next_review 2026-09-29, Feynman: —
- **Mistakes ledger:** the 2026-09-19 row stays active, retries 0, next retry 2026-09-29. The sequential-mantra slip (adding yesterday's posterior) did NOT recur; the new failure mode is counts-by-outcome-type vs total count.
- **Calibration:** keep the outcome-type discipline — successes go to the first parameter, failures to the second, and a count with no outcome attached belongs to neither. Planned retest 2026-09-29: heads-only vs mixed counts (2 heads + 1 tail must land at Beta(a+2, b+1), never Beta(a+3, b+3)).
