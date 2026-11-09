# Review — Naive Bayes — 2026-09-28

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** definitional (free recall)
- **Why this slot:** due review (Attempts.json next_review 2026-09-28) with a live ledger row (2026-09-21, `active`, due 2026-09-28).
- **Question:** Free recall — state the conditional-independence assumption and what multiplies in the numerator.
- **Learner answer:** "it assumes conditional independence of an event once the class is given. it multiplies the prior and the likelihood."
- **Verdict:** FAIL — grade-audit agreed (item 3). Why: the assumption half is correct (features conditionally independent once the class is given), but "the prior and the likelihood" (singular) omits that every per-feature likelihood multiplies — numerator = prior × P(f1 given class) × P(f2 given class) × … — and the denominator is identical across classes, so the decision rule is argmax of the numerator.
- **Repair given in-session:** "naive" = each feature contributes its own little independent likelihood, all multiplied.
- **Attempts.json:** mastery 0.11, interval_index 0, next_review 2026-10-01, Feynman: fail.
- **Mistakes ledger:** existing 2026-09-21 row stays `active` (retries 0) with an update note; NEW 2026-09-28 row (error_type: structural), status `active`, retries 0, next retry 2026-10-01.
- **Retest target:** the numerator rule (prior × every per-feature likelihood, all multiplied) plus the argmax/denominator half — not re-tested in-session.
