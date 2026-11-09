# Review — Learning-rate Schedules (four types) — 2026-09-17

- **Type:** discriminative (Last Q Type was definitional) — due-mistake re-test (retries due 2026-09-13 / 2026-09-17).
- **Quiz-audit:** cycle 1 ISSUES (2 high: floor number + word 'cosine' leaked in stem; 1 medium: contradictory wording) → fixed; cycle 2 ISSUES (1 high: example format echoed exact answer) → example swapped to placeholders, 2-cycle cap reached, emitted with fix.
- **Question:** Three eta-vs-t curves: (A) starts near 0, ramps UP early, then decays to a nonzero floor; (B) decays as eta <- eta*0.999 each step, toward 0, no floor; (C) starts high, slow-fast-slow decrease, flattens to a nonzero floor. Which is warmup / exponential / cosine, and the cosine floor value from the lesson drill?
- **Learner answer:** warmup=A, exp=B, cosine=C correct; floor = 'a very small positive number (but i dont remember the exact number)'.
- **Verdict: FAIL** (claimed pass; grade-audit ISSUES/disagree → correct_verdict fail used). Mapping repair is real, but the asked-for drill value (0.05) was missed — recurrence of the 09-10 floor-value slip.
- **Feedback given:** cosine floor eta_min = 0.05.
- **State:** attempt fail → mastery 0.25, next review 2026-09-21. New Mistakes row (deviation, active, retry 2026-09-21).
