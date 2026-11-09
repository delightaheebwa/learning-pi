# Review — MLE vs MAP Estimation — 2026-09-19

- **Q (discriminative, quiz-audit PASS):** MAP is MLE times a prior — which prior gives L2 vs L1, and why does that pairing hold? One phrase per pairing.
- **A:** Gaussian -> L2, Laplace -> L1; L1 adds a 1 and normalizes to keep probabilities in [0,1]; Gaussian uses average as prior.
- **Grade: FAIL (grade-audit agreed).** Mapping named, both rationales wrong.
- **Repair:** MAP = MLE x prior, and the prior's log IS the penalty — log-Gaussian = squared penalty (L2), log-Laplace = absolute-value penalty (L1).
- **State:** Attempts fail → mastery 0.19, interval_index 0, next_review 2026-09-22. New Mistakes row (active, 2026-09-19).
