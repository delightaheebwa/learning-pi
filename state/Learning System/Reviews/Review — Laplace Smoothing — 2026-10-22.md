# Review — Laplace Smoothing — 2026-10-22

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** `discriminative`
- **Why this slot:** scheduled due review — Attempts.json `next_review` was 2026-10-21 (last reviewed 2026-09-21), picked as one of the scheduled due review slots. Question type: `discriminative`.
- **Question (discriminative):** Scenario: Vocabulary-based text classifier trained over lexicon of $V=4000$ unique words. In training for $C_1$, word $w$ count is 0, out of $N=1000$ total words. (a) What happens to $\log P(\text{document}|C_1)$? (b) Adding pseudocount +1 to $w$, how must denominator be updated across lexicon, and what is $P(w|C_1)$? (c) Decoy: why is adding +1 to continuous reading time feature invalid, and what mathematical object should be used?
- **Learner answer (verbatim):** "(a) Probability of zero collapses product to zero. (b) Must be normalized. Smoothed prob = 1/1000. (c) Not discrete data, unsure of mathematical object."
- **Expected:** (a) $\log(0) = -\infty$ kills the log-likelihood sum. (b) Denominator must add $|V|=4000$ across all word types: $N + |V| = 1000 + 4000 = 5000$. Smoothed prob $P(w|C_1) = (0+1)/(1000+4000) = 1/5000 = 0.0002$. (c) Continuous features do not have discrete counts/lexicon size; likelihood is modeled by a continuous Probability Density Function (PDF) / Gaussian likelihood.
- **Verdict:** **FAIL** — grade-audit agreed. Omitted $|V|$ from denominator (kept denominator at 1000); recognized continuous vs discrete distinction but could not recall PDF / continuous density function.
- **Proof-of-work:** none.
- **Feynman explain-back:** pass carried from prior attempt.
- **Attempts.json:** one attempt recorded 2026-10-22 — `fail` (discriminative, `hunch`, hints 0). Net state: mastery **0.50** advisory, `interval_index` 3 $\rightarrow$ **2** (concept schedule 14d), `next_review` 2026-10-21 $\rightarrow$ **2026-11-05**, `consecutive_correct` **0**, `consecutive_wrong` **1**, Feynman `pass`.
- **Mistakes ledger:** new structural mistake row opened (2026-10-22, `structural`, `active` / retries 0 / next retry 2026-11-05).
- **Active Concepts:** row synced — `last_reviewed` 2026-09-21 $\rightarrow$ **2026-10-22**; `next_review` 2026-10-21 $\rightarrow$ **2026-11-05**; `Last Q Type` definitional $\rightarrow$ **discriminative**; mastery 0.50 advisory noted.
- **Advisory mastery:** **0.50** — Feynman: pass.
- **Carry-forward:** zero-collapse captured; denominator $|V|$ addition ($N+|V|$) and continuous PDF modeling to be re-tested in next retry.
