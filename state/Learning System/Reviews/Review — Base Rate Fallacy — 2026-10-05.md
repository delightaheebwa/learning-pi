# Review — Base Rate Fallacy — 2026-10-05

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** discriminative (MCQ)
- **Why this slot:** priority-1 due mistake — the 2026-09-19 ledger row (`review`, retries 1, next retry 2026-10-05) was the second due mistake in the queue (`ops.py queue aiefs --date 2026-10-05`).
- **Question:** (discriminative MCQ, as recorded in the session transcript) "Which statement commits the base rate fallacy?" — learner-visible option C as recorded: it equates 99% test accuracy with 99% P(correct | positive).
- **Learner answer (verbatim):** "C."
- **Verdict:** PASS — grade-audit agreed. Why: C is the canonical flip — it reads a 99%-accurate test as 99% P(correct | positive) and ignores how common or rare the event is (on a 1/1000 prevalence the positive is mostly wrong). The prior/conditional reversal that opened this row (2026-09-19: `P(+|D)` confused for `P(D|+)`) did not recur.
- **Feynman explain-back:** none offered (`feynman: none`); the row's existing Feynman flag stays `fail`.
- **Attempts.json:** pass → mastery 0.75, interval_index 3, next_review 2026-11-04, q_type `discriminative`.
- **Mistakes ledger:** the 2026-09-19 row advances `review` → `graduated` (retries 2, second consecutive correct; next retry realigned to 2026-11-04).
- **Carry-forward:** Last Q Type is now `discriminative`; the open half is the Feynman explain-back (`fail` — the two halves were not re-articulated in the learner's own words this session).
