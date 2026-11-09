# Review — Optimizer Selection (Rohit heuristic) — 2026-10-10

- **Track/Source:** aiefs — Rohit P1 L08 + handwritten notes 2026-09-10 (Python)
- **Type:** concept · **Q type:** discriminative (MCQ) + the mandatory Feynman explain-back
- **Why this slot:** due review (Attempts.json `next_review` 2026-10-10) — one of the three scheduled reviews in the deterministic queue (digest `review-01a126e4-8923-7272-af26-c75a307b5737-aiefs.json`, used verbatim). Question type per the digest: `discriminative`.
- **Question 1 (discriminative MCQ):** what is the actual reason Adam is the default? **(C)** per-weight adaptive step sizes from the first and second gradient moments.
- **Learner answer:** "C"
- **Verdict:** **PASS** — graded mechanically with `ops.py grade-mcq --key C --answers C`; grade-audit agreed.
- **Question 2 — Feynman explain-back (mandatory beat for a `concept` row, P1.1):** learner: "the default setting is to use Adam and you reach for something else like SGD with momnentum for cases where there are many saddle points or narrow valleys in order to get faster training." → **FAIL**, **`feynman_fail`** (grade-audit agreed). Why: the switch-away-from-Adam reason mismatches the source — the heuristic switches to SGD+momentum for best **final accuracy** with more tuning budget (sharp vs flat minima), and the narrow-valley speed result was a Rosenbrock hyperparameter artifact, not generalizable. The step-3 AdamW (decoupled weight decay) for transformers was missing.
- **Attempts.json:** two attempts recorded 2026-10-10 — `pass` (discriminative, `sure`, hints 0) then `fail` (explain-back, `sure`, hints 0, Feynman fail). Net state: mastery **0.56** advisory, `interval_index` 3 → **2**, `next_review` 2026-10-10 → **2026-10-24** (concept +14d), `consecutive_correct` 0, `consecutive_wrong` **1**, Feynman **fail**.
- **Mistakes ledger:** **one new row** (2026-10-10, `structural`, `active`, retries 0, next retry 2026-10-24) for the Feynman switch-when/why failure, self-attribution from the close envelope. No other row touched.
- **Active Concepts:** row synced — `last_reviewed` 2026-09-10 → **2026-10-10**; `next_review` 2026-10-10 → **2026-10-24**; `Last Q Type` definitional → **discriminative**; mastery noted.
- **Advisory mastery:** **0.56** — Feynman: `fail`.
- **Carry-forward:** the MCQ half holds; the open half is the heuristic's *switch-when/why* — SGD+momentum for best final accuracy with more tuning budget (sharp vs flat minima), plus the AdamW-for-transformers step.
