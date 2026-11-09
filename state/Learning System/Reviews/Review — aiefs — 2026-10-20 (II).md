# Review — aiefs — 2026-10-20 (II)

- **Track:** aiefs
- **Date:** 2026-10-20 (second review session of the day)
- **Concepts Reviewed (4):**
  1. **Conditional Independence** (`concept` · priority-1 due mistake): Initial item FAIL (discriminative — inverted screening-off direction on MCQ, chose D: observing X completely determines class Z, describing determinism rather than conditional independence). Micro-check PASS (spam filter screening-off confirmed: knowing 'free' does not increase probability of 'money' once spam status is known). Net attempts: `fail`, `pass`. Mastery 0.60, `interval_index` 2 $\rightarrow$ 1 $\rightarrow$ 2, `next_review` 2026-11-03. 2026-09-21 mistake row stays `review` (retries 2, next retry 2026-11-03).
  2. **Variance & Covariance** (`concept` · priority-1 due mistake): PASS (discriminative — recognized that centering shifts the origin while leaving covariance matrix and off-diagonal co-movements intact, whereas projecting into the eigenbasis rotates coordinates to zero off-diagonals with eigenvalues $\lambda_i$ on the diagonal). Net attempt: `pass`. Mastery 0.90, `interval_index` 3 $\rightarrow$ 3 (cap 30d), `next_review` 2026-11-19. 2026-09-26 mistake row advances from `active` to `review` (retries 0 $\rightarrow$ 1, next retry 2026-11-19).
  3. **Saddle Points (critical point triage)** (`concept` · scheduled due review): Initial item FAIL (transfer-far — classified saddle point and zero gradient stall correctly, but claimed loss decreases along direction with most variance, conflating PCA data variance with loss Hessian curvature). Micro-check PASS (positive eigenvalue +3.5 increases loss, negative eigenvalue -2.8 decreases loss). Net attempts: `fail`, `pass`. Mastery 0.65, `interval_index` 3 $\rightarrow$ 2 $\rightarrow$ 3, `next_review` 2026-11-19. New structural mistake row opened (`review`, retries 1, next retry 2026-11-19).
  4. **Cosine Similarity** (`concept` · scheduled due review): Initial item FAIL (transfer-far — calculation skipped and cosine vs Euclidean angle/magnitude distinction was unanchored). Micro-check PASS ($\cos([1,1],[5,5]) = 1$). Net attempts: `fail`, `pass`. Mastery 0.65, `interval_index` 3 $\rightarrow$ 2 $\rightarrow$ 3, `next_review` 2026-11-19. New structural mistake row opened (`review`, retries 1, next retry 2026-11-19).

- **Summary Statistics:**
  - Concepts: 4 (1 pass / 3 fail per concept on initial items; 1 pass / 3 fail overall)
  - Graded Items: 7 items total (4 pass / 3 fail across initial items and micro-checks)
  - Mistakes: 2 new mistake rows (Saddle Points, Cosine Similarity); 2 existing mistake rows updated (Variance & Covariance advanced active $\rightarrow$ review; Conditional Independence stays review)
  - State Sync: `Attempts.json` and `📚 Active Concepts.md` synced for all 4 concepts.
