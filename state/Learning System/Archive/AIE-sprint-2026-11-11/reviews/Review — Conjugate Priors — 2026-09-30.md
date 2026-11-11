# Review — Conjugate Priors — 2026-09-30

- **Track/Source:** aiefs — Rohit P1 L07 + Think Bayes (Python)
- **Type:** concept · **Q type:** definitional (free recall)
- **Why this slot:** due review (Attempts.json next_review 2026-09-29, mastery 0.19); the 2026-09-19 ledger row (`active`) had a planned heads-only-vs-mixed-counts retest.
- **Question:** Definitional free recall — define conjugacy and state its practical benefit.
- **Learner answer:** "it means the prior is in the same distribution as the likelihood. the practical benefit is that updating beliefs is a mere addition operation."
- **Verdict:** FAIL — grade-audit agreed (batch verdict agrees: true, item 4). Why: conjugacy pairs the prior with the POSTERIOR (both in the same distribution family — e.g. Beta prior + Binomial likelihood → Beta posterior), not the prior with the likelihood; and the benefit is a closed-form algebraic parameter update with no integrals or sampling, not "mere addition" (Beta–Binomial happens to look like addition — a special case, not the definition).
- **Informal follow-up (NOT tallied as a grade):** the reviewer ran one micro-check — Gamma(2,3) prior + Poisson likelihood. Learner: "yes it comes out in the gamma family. i think the counts are summed to a and b." Family recognition is correct; the placement is wrong (it imports the Beta–Binomial pattern). Correct Gamma–Poisson bookkeeping: Σx_i adds to the shape a; the number of observations n adds to the rate b. Verifier: micro-check grade-audit (run 6b656950, agrees: true; placement half FAIL). The learner then declined the third placement question and asked to close ("i think do the file writes. lets ignore the micro check."), so this micro-check produced no Attempts.json entry and does not change the tally (4 pass / 1 fail).
- **Repair given in-session:** prior↔posterior family pairing; the benefit stated as a closed-form algebraic update; the Gamma–Poisson slot table (Σx_i → shape, n → rate).
- **Attempts.json:** mastery 0.11, interval_index 0, next_review 2026-10-03, Feynman: — (no Feynman item this session).
- **Mistakes ledger:** 2026-09-19 row stays `active`, retries 0, next retry realigned to 2026-10-03 (Attempts.json); NEW 2026-09-30 structural row (the definition/benefit fail plus the Gamma–Poisson placement slip).
- **Retest target:** prior↔posterior family pairing (Beta–Binomial) + the Gamma–Poisson slot bookkeeping; the heads-only-vs-mixed-counts item is still unrun.
