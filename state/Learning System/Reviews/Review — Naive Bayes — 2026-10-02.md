# Review — Naive Bayes — 2026-10-02

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** due review (Attempts.json next_review 2026-10-01, mastery 0.11) with two due ledger rows (2026-09-21 and 2026-09-28, both `active`, next retry 2026-10-01).
- **Question:** Discriminative MCQ — why does Naive Bayes multiply the per-feature likelihoods and compare numerators only? **(B)** the features are conditionally independent given the class, and the denominator is identical for every class.
- **Learner answer:** "B."
- **Verdict:** PASS — grade-audit agreed. Why: B states both halves in one line — the conditional-independence assumption (given the class) and its consequence (the shared denominator, so the decision rule is argmax of the numerator). The 2026-09-28 row failed exactly this second half (numerator given as "it multiplies the prior and the likelihood", singular); it did not recur.
- **Feynman explain-back:** FAIL — verifier agreed. The explain-back described generic Bayesian belief-updating/uncertainty, with no conditional-independence assumption, no when/why, and no example. Feynman flag stays `fail`.
- **Attempts.json:** mastery 0.50, interval_index 1, next_review 2026-10-09, Feynman: fail (this session).
- **Mistakes ledger:** both open rows advance — 2026-09-21 → `review`, retries 1; 2026-09-28 → `review`, retries 1; next retry 2026-10-09 (Attempts.json) for both.
- **Carry-forward:** Last Q Type is now `discriminative`; the open halves are the Feynman explain-back (definition + when/why + example) and the concept's low mastery (0.11 → 0.50).
