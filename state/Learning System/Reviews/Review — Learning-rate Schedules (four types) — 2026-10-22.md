# Review — Learning-rate Schedules (four types) — 2026-10-22

- **Track/Source:** aiefs — Rohit P1 L08 + Ruder + handwritten notes 2026-09-10 (Python)
- **Type:** concept · **Q type:** `definitional`
- **Why this slot:** priority-1 due mistake retry — ledger rows (2026-09-10 ×2, 2026-09-17) due 2026-10-21. Question type: `definitional` + perturbation proof-of-work.
- **Question (definitional + perturbation PoW):** Run A (warmup + cosine decay to $\eta_{\min}=10^{-5}$), Run B (exponential decay $\eta_t = \eta_0 \cdot (0.999)^t$). (a) Identify structural family and discriminators. (b) Perturbation: asymptotic limit of Run B; exact $\eta_{\min}$ for Run A; what happens to step size at $t=T$ if $\eta_{\min}=0$, and why is positive floor desirable for fine-tuning?
- **Learner answer (verbatim):** "(a) Run A = Cosine annealing, Run B = Exponential. Run A starts at baseline, increases then decays to set baseline. Run B starts at max then decays towards zero. (b) Run B approaches zero. eta_min = 10^-5. If set to zero then learning takes much longer hence fine tuning would take longer since the step size small."
- **Expected:** (a) Cosine annealing (warmup ramp + smooth cosine decay to nonzero floor) vs Exponential decay (starts at max, geometric decay without floor). (b) Run B $\rightarrow 0$. Run A $\eta_{\min} = 10^{-5}$. If $\eta_{\min} = 0$, at $t=T$, $\cos(\pi) = -1$ so $\eta_T = 0$ exactly: parameter updates cease entirely (model freezes), not merely slow down. A strictly positive floor prevents optimizer stall during late fine-tuning.
- **Verdict:** **FAIL** — grade-audit agreed. Recognized small step size but missed that $\eta_T$ hits exactly 0 when $\eta_{\min}=0$, halting parameter updates completely (freezing).
- **Proof-of-work:** perturbation — **fail** (did not deduce parameter update cessation $\Delta \theta = 0$ at $t=T$).
- **Feynman explain-back:** — (not elicited).
- **Attempts.json:** one attempt recorded 2026-10-22 — `fail` (definitional, `hunch`, hints 0). Net state: mastery **0.40** advisory, `interval_index` 3 $\rightarrow$ **2** (concept schedule 14d), `next_review` 2026-10-21 $\rightarrow$ **2026-11-05**, `consecutive_correct` **0**, `consecutive_wrong` **1**, Feynman `—`.
- **Mistakes ledger:** new structural mistake row opened (2026-10-22, `structural`, `active` / retries 0 / next retry 2026-11-05); existing rows (2026-09-10 ×2, 2026-09-17) realigned to 2026-11-05.
- **Active Concepts:** row synced — `last_reviewed` 2026-09-21 $\rightarrow$ **2026-10-22**; `next_review` 2026-10-21 $\rightarrow$ **2026-11-05**; `Last Q Type` discriminative $\rightarrow$ **definitional**; mastery 0.40 advisory noted.
- **Advisory mastery:** **0.40** — Feynman: —.
- **Carry-forward:** curve shape discriminators and $\eta_{\min}=10^{-5}$ recalled cleanly; exact zero step size $\eta_T = 0$ / optimizer freeze at $\eta_{\min}=0$ to be targeted in next retry.
