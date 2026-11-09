# Review — Adam (adaptive moments) — 2026-10-20

- **Track/Source:** aiefs — Rohit P1 L08 + Kingma & Ba 2015 + Ruder + handwritten notes 2026-09-08 (Python)
- **Type:** procedure · **Q types:** `discriminative` (priority-1 mistake retry), then `micro-check`
- **Why this slot:** priority-1 due mistake — the 2026-09-26 and 2026-10-03 ledger rows (next retry 2026-10-13, Attempts.json) carried the concept into the queue (digest `Learning System/.tmp/review-session-aiefs.json`, used verbatim; `due_mistakes: 2`, `due_reviews: 3`). Question type per the digest: `discriminative`.
- **Question (discriminative):** specify Adam's two running averages ($m_t$ and $v_t$), what each is a mean of, and what cold-start problem the bias-correction hats solve.
- **Learner answer (initial):** $m_t$ direction and $v_t$ scale captured; but $v_t$ specified as percentage of gradient sizes instead of squared gradients $g^2$; cold-start attributed to gradients reset rather than zero-initialization.
- **Verdict:** **FAIL** — grade-audit agreed. Why: $v_t$ is the running average of **squared** gradients (RMSProp heritage, scale), not a percentage of gradient sizes; cold-start is caused by zero-initialization ($m_0 = 0, v_0 = 0$) pulling early estimates towards zero (timid steps), not a gradient reset.
- **Micro-check (PASS, grade-audit agreed):** computation check on bias-corrected moment estimate $\hat{m}_1$ at step $t=1$ with $g_1 = 0.4$, $\beta_1 = 0.9$ $\rightarrow$ raw $m_1 = 0.1 \times 0.4 = 0.04$ (10% of gradient), $\hat{m}_1 = 0.04 / (1 - 0.9^1) = 0.4$ $\rightarrow$ answered $\hat{m}_1 = 4$ (scale match) / raw ratio 10% correct.
- **Feynman explain-back:** **exempt** (`procedure` row, P1.1).
- **Attempts.json:** two attempts recorded 2026-10-20 — `fail` (discriminative, `sure`, hints 0), `pass` (micro-check, `sure`, hints 0). Net state: mastery **0.50** advisory, `interval_index` 0 $\rightarrow$ 0 $\rightarrow$ **1**, `next_review` 2026-10-13 $\rightarrow$ **2026-10-27** (procedure +7d), `consecutive_correct` **1**, `consecutive_wrong` **0**, Feynman `—` (exempt).
- **Mistakes ledger:** one **new** row (2026-10-20, `structural`, `review` / retries 1 / next retry 2026-10-27); existing 2026-09-26 and 2026-10-03 rows updated with a note pointing to the new row and next retry realigned to 2026-10-27.
- **Active Concepts:** row synced — `last_reviewed` 2026-10-10 $\rightarrow$ **2026-10-20**; `next_review` 2026-10-13 $\rightarrow$ **2026-10-27**; `Last Q Type` definitional $\rightarrow$ **discriminative**; mastery 0.50 advisory noted.
- **Advisory mastery:** **0.50** — Feynman: exempt.
- **Carry-forward:** post-fail micro-check passed; the zero-initialization rationale for the hats and $v_t$ as squared gradients must be reinforced in the next retry.
