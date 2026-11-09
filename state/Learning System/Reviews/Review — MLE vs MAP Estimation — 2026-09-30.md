# Review — MLE vs MAP Estimation — 2026-09-30

- **Track/Source:** aiefs — Rohit P1 L07 + lesson 2026-09-05 (Python)
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** priority-1 due mistake — the 2026-09-14 ledger row (`review`, retries 1, next retry 2026-09-30) was the second-oldest due mistake; the item re-tests the Gaussian↔L2 / Laplace↔L1 mapping that both ledger rows failed on.
- **Question:** Discriminative MCQ — a Laplace prior on a Gaussian likelihood puts which penalty on the parameters (choose A–D)?
- **Learner answer:** "A."
- **Verdict:** PASS — grade-audit agreed (batch verdict agrees: true, item 2). Why: A is the L1 / absolute-value penalty, which is exactly what a Laplace prior's log-density contributes; the Gaussian↔L2 / Laplace↔L1 mapping came back with its rationale (squared vs absolute follows the log-density's shape) offered spontaneously. The MCQ did not demand the −log p(θ) derivation, so the shape argument was volunteered rather than tested.
- **Attempts.json:** mastery 0.75, interval_index 3, next_review 2026-10-30, Feynman: fail (carried — no Feynman item this session).
- **Mistakes ledger:** both rows (2026-09-14 and 2026-09-19) → `graduated`, retries 2 (second consecutive correct after the 2026-09-23 pass).
- **Carry-forward:** Last Q Type is now `discriminative`; the Feynman flag (`fail` since 2026-09-23) remains the open half of this concept.
