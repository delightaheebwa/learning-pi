# Review — Entropy (Average Surprise) — 2026-09-24

- **Track/Source:** aiefs — Rohit P1 L09 + Olah (Python)
- **Type:** concept · **Q type:** definitional
- **Why this slot:** priority-1 due mistake; the entropy sign row was due 2026-09-17.
- **Question:** For P = (0.5, 0.25, 0.25), compute entropy on paper and explain where each p appears twice, when to use H(P) instead of cross-entropy, and the nearest-neighbour distinction.
- **Learner answer:** "i would use entropy when i want to find out the floor value based on the data. the neighbor nearest to another has low cross entropy."
- **Verdict:** FAIL — grade-audit agreed. The requested 1.5-bit result and the two appearances of p were omitted; the answer also misstated the entropy/cross-entropy relationship.
- **Attempts.json:** mastery 0.45, interval_index 0, next_review 2026-09-28, Feynman: fail
- **Mistakes ledger:** existing entropy sign row returned to `active`, retries 0, next retry 2026-09-28.
- **Repair target:** H(P) = -sum p_i log_2 p_i; p_i is both the surprise generator inside the log and the weight outside; H(P) is one-distribution uncertainty, while cross-entropy compares distributions.
