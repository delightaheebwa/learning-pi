# Review — Sequential Bayesian Updating — 2026-10-20

- **Track/Source:** aiefs — Rohit P1 L07 (Python)
- **Type:** concept · **Q types:** `discriminative`, then `micro-check`
- **Why this slot:** scheduled due review — Attempts.json `next_review` was 2026-10-16 (digest `Learning System/.tmp/review-session-aiefs.json`, used verbatim; `due_reviews: 3`). Question type per the digest: `discriminative`.
- **Question (discriminative):** explain the relationship between prior and posterior across sequential observations, and explain how batch updating compares to sequential updating.
- **Learner answer (initial):** claimed adding yesterday's prior to today's posterior; missed order invariance / identical batch vs sequential updating.
- **Verdict:** **FAIL** — grade-audit agreed. Why: yesterday's posterior BECOMES today's prior (slotting into the prior slot), not adding the prior to the posterior; Bayesian updating is strictly order-invariant (updating on data sequentially yields the exact same posterior as updating on the whole batch at once).
- **Micro-check (FAIL, grade-audit agreed):** order invariance test — recognized order invariance conceptually that both yield the same result, but when asked for updated Beta parameters starting from prior $\text{Beta}(1,1)$ after 2 heads and 2 tails, gave raw data counts $(2,2)$ instead of adding counts to prior parameters to yield $\text{Beta}(3,3)$.
- **Feynman explain-back (P1.1):** not elicited (gap surfaced).
- **Attempts.json:** two attempts recorded 2026-10-20 — `fail` (discriminative, `sure`, hints 0), `fail` (micro-check, `sure`, hints 0). Net state: mastery **0.28** advisory, `interval_index` 3 $\rightarrow$ 2 $\rightarrow$ **1**, `next_review` 2026-10-16 $\rightarrow$ **2026-10-27** (concept +7d), `consecutive_correct` **0**, `consecutive_wrong` **2**, Feynman `None`.
- **Mistakes ledger:** one **new** row (2026-10-20, `structural`, `active` / retries 0 / next retry 2026-10-27). This concept had no previous mistake rows.
- **Active Concepts:** row synced — `last_reviewed` 2026-09-16 $\rightarrow$ **2026-10-20**; `next_review` 2026-10-16 $\rightarrow$ **2026-10-27**; `Last Q Type` definitional $\rightarrow$ **discriminative**; mastery 0.28 advisory noted.
- **Advisory mastery:** **0.28** — Feynman: none.
- **Carry-forward:** double fail on both initial item and micro-check. Needs explicit re-derivation: (1) yesterday's posterior is today's prior, (2) order invariance, (3) $\text{Beta}(a+h, b+t)$, adding to the prior parameters rather than outputting raw counts.
