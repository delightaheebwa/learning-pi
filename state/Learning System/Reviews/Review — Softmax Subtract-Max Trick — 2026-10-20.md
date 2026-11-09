# Review — Softmax Subtract-Max Trick — 2026-10-20

- **Track/Source:** aiefs — Rohit P1 L06 + Gundersen (Python)
- **Type:** procedure · **Q type:** `discriminative`
- **Why this slot:** scheduled due review — Attempts.json `next_review` was 2026-10-15 (last reviewed 2026-10-08), picked as one of the scheduled review slots (digest `Learning System/.tmp/review-session-aiefs.json`, used verbatim; `due_reviews: 3`). Question type per the digest: `discriminative`.
- **Question (discriminative):** what failure mode does subtracting $\max(z)$ prevent, how does mathematical invariance hold, and what is the exponent of the largest shifted logit?
- **Learner answer (verbatim):** PASS — correctly identified float overflow prevention, mathematical invariance via logit translation cancellation ($\exp(z_i - c) / \sum \exp(z_j - c) = \exp(z_i)/\sum \exp(z_j)$), and largest logit exponent $z_{\max} - \max(z) = 0 \Rightarrow e^0 = 1$.
- **Verdict:** **PASS** — grade-audit agreed. All three components (overflow prevention, shift cancellation invariance, and zero exponent / $e^0=1$) correctly explained.
- **Feynman explain-back:** **exempt** (`procedure` row, P1.1).
- **Attempts.json:** one attempt recorded 2026-10-20 — `pass` (discriminative, `sure`, hints 0). Net state: mastery **0.75** advisory, `interval_index` 1 $\rightarrow$ **2** (procedure ladder capped at +14d), `next_review` 2026-10-15 $\rightarrow$ **2026-11-03**, `consecutive_correct` **2**, `consecutive_wrong` **0**, Feynman `—` (exempt).
- **Mistakes ledger:** 2026-09-26 structural row graduates (`review` $\rightarrow$ `graduated`, retries 2, second consecutive correct recall); 2026-10-05 deviation row Next Retry realigned to 2026-11-03.
- **Active Concepts:** row synced — `last_reviewed` 2026-10-08 $\rightarrow$ **2026-10-20**; `next_review` 2026-10-15 $\rightarrow$ **2026-11-03**; `Last Q Type` definitional $\rightarrow$ **discriminative**; mastery 0.75 advisory noted.
- **Advisory mastery:** **0.75** — Feynman: exempt.
- **Carry-forward:** second consecutive correct recall; 2026-09-26 mistake row graduated; concept sits at procedure interval cap (+14d).
