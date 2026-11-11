# Review — Likelihood — 2026-09-28

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** definitional (free recall)
- **Why this slot:** due review (Attempts.json next_review 2026-09-28) with a live ledger row (2026-09-17, `review`, due 2026-09-28).
- **Question:** Free recall — define likelihood and name P(free appears | spam).
- **Learner answer:** "how probable is a certain event given a certain class. P(free appears|spam) is called the evidence."
- **Verdict:** FAIL — grade-audit agreed (item 5). Why: the verbal definition of likelihood is fine, but P(feature | class) IS the likelihood; the evidence is the denominator P(features), marginalised over all classes and therefore identical for every class.
- **Repair given in-session:** P(feature | class) = likelihood; P(features) = evidence / normalizer.
- **Attempts.json:** mastery 0.39, interval_index 0, next_review 2026-10-01, Feynman: fail.
- **Mistakes ledger:** 2026-09-17 row returns to `active` (retries 0, next retry 2026-10-01) — the fail was a different slip (evidence label rather than the fixed/varied half, which was not re-tested); NEW 2026-09-28 row (error_type: structural), status `active`, retries 0, next retry 2026-10-01.
- **Retest target:** the likelihood/evidence split (P(feature | class) vs P(features)) together with the fixed/varied definition.
