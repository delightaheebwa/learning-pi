# Review — Likelihood — 2026-10-02

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** priority-1 due mistake — the 2026-09-17 ledger row (`active`, retries 0, next retry 2026-10-01) was the second-oldest due mistake; the 2026-09-28 evidence-label row was also due (next retry 2026-10-01).
- **Question:** Discriminative MCQ — role-matching in the spam Bayes formula P(spam | f1…fn) = P(spam)·P(f1|spam)…P(fn|spam) / P(f1…fn): which factor is the evidence, which the likelihood, which the posterior? **(A)** evidence = P(f1…fn), identical for every class; P(fi|spam) = likelihood; P(spam|f) = posterior.
- **Learner answer:** "A."
- **Verdict:** PASS — grade-audit agreed. Why: A puts the evidence in the shared denominator P(f1…fn) (marginalised over classes, therefore identical for every class), names P(fi|class) as the likelihood and P(class|f) as the posterior — precisely the distinctions the 2026-09-28 slip inverted when it labelled P(feature | class) "the evidence". The 2026-09-28 evidence-slip was answered correctly this time.
- **Feynman explain-back:** FAIL — verifier agreed. The explain-back said "probability an event will happen given a class", gave no fixed/varied articulation (θ is what varies, D is fixed), named the evidence without the P(D|θ)-vs-P(D) distinction, and offered no example. Feynman flag stays `fail`.
- **Attempts.json:** mastery 0.65, interval_index 1, next_review 2026-10-09, Feynman: fail (this session).
- **Mistakes ledger:** both open rows advance — 2026-09-17 → `review`, retries 1; 2026-09-28 → `review`, retries 1; next retry 2026-10-09 (Attempts.json) for both.
- **Carry-forward:** Last Q Type is now `discriminative`; the open halves are the Feynman explain-back and the fixed/varied definition (not re-tested this session).
