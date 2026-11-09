# Review — Softmax Subtract-Max Trick — 2026-09-26

- **Track/Source:** aiefs — Rohit P1 L06 + Gundersen (Python)
- **Type:** procedure · **Q type:** definitional (free recall)
- **Why this slot:** due review; first graded retrieval of the overflow rationale and the identical-result half since the L06 teaching.
- **Question:** What can go wrong computing softmax directly with exp(z_i) on large logits, and does subtracting max(z) change the final probabilities?
- **Learner answer:** "you can end up with infinite probabilities. subtracting helps to keep them bounded so they wont go off the rails into infinity."
- **Verdict:** FAIL — grade-audit agreed. Two missing halves: (1) the actual failure is exp overflow → +inf → inf/inf = NaN (not "infinite probabilities"); (2) the identical-result half — exp(−c) cancels between numerator and denominator, so the probabilities are mathematically unchanged (all exponents ≤ 0 after subtraction, max exp = exp(0) = 1, denominator ≥ 1; only ordinary floating-point rounding differs in the last bits).
- **Attempts.json:** mastery 0.50, interval_index 1, next_review 2026-10-03, Feynman: —
- **Mistakes ledger:** NEW 2026-09-26 row (error_type: structural, status active), next retry 2026-10-03.
- **Calibration:** repair delivered in-session and fact-checked (independent fact-check subagent, all claims PASS after one correction of an overstated "byte-for-byte identical" claim). Check-back answered correctly in the learner's own words — "it is 1(exp(0)). it can never overflow because they are now all less than or equal to 0 hence when an exponent is applied to it, it will be in the range (0, 1]" — so the bounded-range picture is in place. Retest both halves: the NaN failure mode and "the probabilities are unchanged".
