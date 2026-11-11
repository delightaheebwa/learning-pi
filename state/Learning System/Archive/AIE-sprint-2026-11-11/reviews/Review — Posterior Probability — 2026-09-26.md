# Review — Posterior Probability — 2026-09-26

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** definitional + computational
- **Why this slot:** due review (row was overdue since 2026-09-24); the 2026-09-17 mistake row is still open.
- **Question:** Name the two factors multiplying in the numerator of P(θ|D) ∝ ___ × ___ and whether the likelihood is the post-data evidence factor or a pre-data guess; then on paper the posterior for P(sick)=0.10, P(+|sick)=0.80, P(+|healthy)=0.20.
- **Learner answer:** "prior and likelihood. likelihood is the post evidence factor." (no numeric posterior given)
- **Verdict:** FAIL — grade-audit agreed: the formula and role halves are correct (the 09-17 prior-doubling and the 09-21 likelihood-role slips did NOT recur), but the explicitly requested numeric posterior was omitted entirely (0.08 / 0.26 ≈ 30.8%).
- **Attempts.json:** mastery 0.11, interval_index 0 (3 consecutive wrong), next_review 2026-09-29, Feynman: pass (from 2026-09-21 explain-back).
- **Mistakes ledger:** the 2026-09-17 row stays active, retries 0, next retry 2026-09-29 — the open half has moved from formula recall (now solid) to computing the number.
- **Calibration:** numerator identification is retrieval-solid; the gap is arithmetic execution. Denominator = total P(+) = both branches (0.08 + 0.18 = 0.26); healthy supplies most positives (9× base rate) — a positive test still leaves ≈31% sick. The prior is a multiplicand, never something you divide by.
