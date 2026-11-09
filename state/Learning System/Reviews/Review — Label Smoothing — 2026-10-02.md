# Review — Label Smoothing — 2026-10-02

- **Track/Source:** aiefs — Rohit P1 L09 + PyTorch CrossEntropyLoss + Inception (Python)
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** due review (Attempts.json next_review 2026-10-01, mastery 0.62) with a due ledger row (2026-09-24, `review`, retries 1, next retry 2026-10-01).
- **Question:** Discriminative MCQ — with K = 5 classes and ε = 0.1, what are the soft targets for the true class and for each other class? **(C)** 0.92 on the true class / 0.02 on each other class (the near-miss 0.9 / 0.025 pair was the distractor).
- **Learner answer:** "C."
- **Verdict:** PASS — grade-audit agreed. Why: 0.92 = (1−ε) + ε/K and 0.02 = ε/K are exactly `soft = (1−ε)·one-hot + ε/K` — the one-hot structure survives scaled by (1−ε), with an ε/K smear over every class — and the 0.9 / 0.025 distractor (reading ε as a straight subtraction instead of the mixture) was not chosen. This is an isomorphic re-run of the 2026-09-24 CP6 P3 slip, where ε was read as the whole target (0.2 everywhere); it did not recur.
- **Attempts.json:** mastery 0.81, interval_index 3, next_review 2026-11-01, Feynman: — (no Feynman item this session).
- **Mistakes ledger:** 2026-09-24 row → `graduated`, retries 2 (second consecutive correct after the 2026-09-24 same-session repair), next retry realigned to 2026-11-01 (Attempts.json).
- **Carry-forward:** Last Q Type is now `discriminative`; the Active Concepts row's open question on a principled adaptive ε (distillation vs the Adam analogy) stays open.
