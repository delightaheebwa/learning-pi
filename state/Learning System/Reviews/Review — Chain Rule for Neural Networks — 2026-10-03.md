# Review — Chain Rule for Neural Networks — 2026-10-03

- **Track/Source:** aiefs — Rohit P1 L05 + CS231n (Python)
- **Type:** procedure · **Q type:** discriminative
- **Why this slot:** due review (Attempts.json next_review 2026-10-03, interval_index 1, consecutive_wrong 1) with the 2026-09-26 `active` ledger row (application, retries 0) — the planned mechanism-retest slot.
- **Question:** Why does backprop multiply gradients going backward instead of adding them, and what happens to the gradient when it passes through a layer whose local gain ≈ 0?
- **Learner answer:** "it multiplies instead of adding because all the layers are dependent on one another. the gradient becomes zero when passing through a layer with local gain approx 0 since we are multiplying not adding."
- **Verdict:** PASS — grade-audit agreed. Why: both halves are right — the multiplication is forced by the functional dependence of the intermediate layers (the chain rule's product of local derivatives), and a local gain ≈ 0 multiplies the running gradient to ≈ 0 (adding would leave it unchanged, which is exactly the contrast the answer draws). The mechanism the 2026-09-26 fused-path answer (2x(x+y)(x²+1) = 100 ≠ 24) missed is now stated.
- **Attempts.json:** mastery 0.72, interval_index 2, next_review 2026-10-17, Feynman: — (none offered).
- **Mistakes ledger:** the 2026-09-26 row moves `active` → `review` (retries 1); next retry realigned to 2026-10-17 (Attempts.json).
- **Carry-forward:** Last Q Type is now `discriminative`; the planned paper re-derivation (nudge-y single path, df/dy = x² = 4) was not run — the mechanism was answered verbally. The open half is a numeric two-path computation under the product rule.
