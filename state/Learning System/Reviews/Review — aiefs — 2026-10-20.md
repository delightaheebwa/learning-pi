# Review — aiefs — 2026-10-20

- **Track:** aiefs
- **Date:** 2026-10-20
- **Concepts Reviewed (5):**
  1. **Adam (adaptive moments)** (`procedure` · priority-1 due mistake): Initial item FAIL (discriminative — missed $v_t$ as mean of squared gradients $g^2$, cold-start attributed to gradients reset rather than zero-initialization). Micro-check PASS ($\hat{m}_1 = 4$, raw ratio 10%). Net attempts: `fail`, `pass`. Mastery 0.50, `interval_index` 0 $\rightarrow$ 1, `next_review` 2026-10-27. New mistake row opened (`review`, retries 1).
  2. **Chain Rule for Neural Networks** (`procedure` · priority-1 due mistake): Initial item FAIL (definitional — evaded branching path combination rule, though partial derivative $\partial f / \partial y = 4$ correct). Micro-check PASS (branching paths add, $df/dx = 7$ at $x=2$). Net attempts: `fail`, `pass`. Mastery 0.65, `interval_index` 2 $\rightarrow$ 1 $\rightarrow$ 2, `next_review` 2026-11-03. New mistake row opened (`review`, retries 1).
  3. **Sequential Bayesian Updating** (`concept` · due review): Initial item FAIL (discriminative — claimed adding yesterday's prior to today's posterior, missed order invariance). Micro-check FAIL (recognized order invariance conceptually, but gave raw data counts (2,2) instead of adding to prior to yield $\text{Beta}(3,3)$). Net attempts: `fail`, `fail`. Mastery 0.28, `interval_index` 3 $\rightarrow$ 2 $\rightarrow$ 1, `next_review` 2026-10-27. New mistake row opened (`active`, retries 0).
  4. **Bayes' Theorem** (`concept` · due review): PASS (discriminative — solid conceptual explanation of rare base-rate dominance causing false positives to outnumber true positives). Net attempt: `pass`. Mastery 1.00, `interval_index` 3 $\rightarrow$ 3 (cap), `next_review` 2026-11-19.
  5. **Softmax Subtract-Max Trick** (`procedure` · due review): PASS (discriminative — correctly identified float overflow prevention, mathematical invariance via logit translation cancellation, and largest logit exponent 0 $\Rightarrow e^0=1$). Net attempt: `pass`. Mastery 0.75, `interval_index` 1 $\rightarrow$ 2, `next_review` 2026-11-03. 2026-09-26 mistake row graduated (`graduated`, retries 2).

- **Summary Statistics:**
  - Concepts: 5 (2 pass / 3 fail per concept on initial items; 2 pass / 3 fail overall)
  - Graded Items: 8 items total (5 pass / 3 fail)
  - Mistakes: 3 new mistake rows (Adam, Chain Rule, Sequential Bayesian Updating); 1 mistake row graduated (Softmax Subtract-Max Trick 2026-09-26)
  - State Sync: `Attempts.json` and `📚 Active Concepts.md` synced for all 5 concepts.
