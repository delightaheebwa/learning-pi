# Review — Softmax Subtract-Max Trick — 2026-10-05

- **Track/Source:** aiefs — Rohit P1 L06 + Gundersen (Python)
- **Type:** procedure · **Q type:** discriminative (MCQ)
- **Why this slot:** due review — Attempts.json `next_review` 2026-10-03 (overdue); its 2026-09-26 ledger row was also due (next retry 2026-10-03) but lost the two priority-1 mistake slots to the older Entropy and Base Rate Fallacy rows, so the concept came through its due-review slot.
- **Question:** (discriminative MCQ, as recorded in the session transcript) "Which claim is FALSE?" — recorded options: A = subtract max(z) before exp to prevent float overflow; B = subtracting max "slightly changes the probabilities"; C = "mathematically identical — max cancels".
- **Learner answer (verbatim):** "C."
- **Verdict:** FAIL — grade-audit agreed. Why: the FALSE claim was **B** — subtracting max(z) is provably identical (the exp(−max z) factor cancels between numerator and denominator), so it does *not* change the probabilities; the learner instead selected C, which is a true identity statement. The transcript records this as a FALSE-vs-TRUE reading slip, not a knowledge gap.
- **Feynman explain-back:** none (`feynman: none`; procedure type, and no explain-back was offered).
- **Repair:** verdict delivered with the T/F-on-paper detector; the learner declined the deep dive ("nope"), so the identity half was not re-tested in-session.
- **Attempts.json:** fail → mastery 0.28, interval_index 0, next_review 2026-10-08, q_type `discriminative`.
- **Mistakes ledger:** NEW 2026-10-05 row — error_type `deviation` (the envelope's `careless` is not in the ledger enum `structural | deviation | application | metacognitive`; canonicalized to the "understood but slipped / misread" class, which is the envelope's own self-attribution), `active`, retries 0, next retry 2026-10-08. The 2026-09-26 row **stays `active`** (retries 0) — its own halves (exp overflow → +inf → inf/inf = NaN; the identical-result half) were not re-tested today — and its next retry is realigned 2026-10-03 → 2026-10-08.
- **Carry-forward:** retest the identical-result half and the T/F polarity on an isomorphic item; the row's NaN failure-mode half is still unproven.
