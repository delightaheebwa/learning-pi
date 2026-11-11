# Review — Conjugate Priors — 2026-09-19

- **Q (definitional, quiz-audit PASS):** What makes a prior conjugate, and state the Beta-Binomial update rule.
- **A:** conjugate = belongs to the same distribution; update = adding yesterday's posterior to today's prior.
- **Grade: FAIL (grade-audit agreed).** Definition loose but directional; the rule is wrong — sequential-updating mantra leaked in.
- **Repair:** conjugacy = posterior stays in the same family as the prior; Beta(a,b) + s/f -> Beta(a+s,b+f) — add OBSERVED COUNTS to the prior parameters.
- **State:** Attempts fail → mastery 0.38, interval_index 0, next_review 2026-09-22. New Mistakes row (active, 2026-09-19).
