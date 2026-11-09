# Review — Perplexity — 2026-10-03

- **Track/Source:** aiefs — Rohit P1 L09 + PyTorch CrossEntropyLoss (Python)
- **Type:** concept · **Q type:** discriminative
- **Why this slot:** due review (Attempts.json next_review 2026-10-03, mastery 0.62) plus its overdue `active` ledger row (2026-09-24, the bits→base conversion slip, next retry 2026-09-27). The row was due but lost both priority-1 mistake slots, so it was covered through a review slot.
- **Question:** Model A reports 2 bits/token and Model B 1 bit/token — give each model's perplexity and say what the number means.
- **Learner answer:** "A->4, B->2. the number is the number of equlaly likely choices the model is hesitating between."
- **Verdict:** PASS — grade-audit agreed. Why: both conversions are right in the **bits** base (2² = 4, 2¹ = 2 — no repeat of the 2026-09-24 e^H-on-a-bits-value slip), and the gloss is the concept's own reading: perplexity = the effective number of equally likely choices the model is hesitating between.
- **Attempts.json:** mastery 0.81, interval_index 3, next_review 2026-11-02, Feynman: — (none offered).
- **Mistakes ledger:** the 2026-09-24 row moves `active` → `review` (retries 1); next retry realigned to 2026-11-02 (Attempts.json). One more consecutive correct graduates it.
- **Carry-forward:** Last Q Type is now `discriminative`. The unit detector ("bits → base 2, nats → base e") held on a fresh bits-valued pair; the nats branch was not exercised.
