# Review — Saddle Points (critical point triage) — 2026-10-20 (II)

- **Track/Source:** aiefs — Rohit P1 L08 + Ruder/Dauphin 2014 + handwritten notes 2026-09-10 (Python)
- **Type:** concept · **Q types:** `transfer-far` (scheduled review), then `micro-check`
- **Why this slot:** scheduled due review (due 2026-10-18, backlog clearance).
- **Question (transfer-far):** classify critical point with mixed Hessian eigenvalues, explain GD behavior, and specify escape direction.
- **Learner answer (initial):** classified saddle point and zero gradient stall correctly, but stated loss decreases along direction with most variance.
- **Verdict:** **FAIL** — grade-audit agreed. Conflated data variance / PCA spread with loss Hessian curvature; loss decreases along directions of negative eigenvalue / negative curvature, not data variance.
- **Micro-check (PASS, grade-audit agreed):** eigenvalue response check on loss: positive eigenvalue +3.5 increases loss / negative eigenvalue -2.8 decreases loss (answered 'it increases for 3.5 but decreases for -2.8').
- **Feynman explain-back:** none.
- **Attempts.json:** two attempts recorded 2026-10-20 — `fail` (transfer-far, `sure`, hints 0), `pass` (micro-check, `sure`, hints 0). Net state: mastery **0.65** advisory, `interval_index` 3 $\rightarrow$ 2 $\rightarrow$ **3**, `next_review` 2026-10-18 $\rightarrow$ **2026-11-19** (concept +30d), `consecutive_correct` **1**, `consecutive_wrong` **0**, Feynman `—`.
- **Mistakes ledger:** new structural mistake row opened (2026-10-20, `structural`, `review` / retries 1 / next retry 2026-11-19).
- **Active Concepts:** row synced — `last_reviewed` 2026-09-17 $\rightarrow$ **2026-10-20**; `next_review` 2026-10-18 $\rightarrow$ **2026-11-19**; `Last Q Type` discriminative $\rightarrow$ **transfer-far**; mastery 0.65 advisory noted.
- **Advisory mastery:** **0.65** — Feynman: —.
- **Carry-forward:** micro-check passed on positive vs negative curvature effect; escape along negative curvature needs reinforcement in next retry.
