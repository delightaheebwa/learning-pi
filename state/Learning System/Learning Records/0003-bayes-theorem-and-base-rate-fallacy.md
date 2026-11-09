# Bayes' Theorem & the Base Rate Fallacy

Learner mastered Bayes' theorem end-to-end and — critically — corrected the base-rate fallacy, the single most load-bearing misconception for later probabilistic ML work. The correction ran the full cycle: likelihood-heavy ("99% test → 99% sure") → prior-heavy ("10% base rate → 10% answer") → a clean, self-checked counting-table computation. This equips the learner to interpret model outputs, set thresholds, and read A/B test results without over- or under-weighting the prior.

**Status:** active
**Evidence:** base-rate climb across 5 attempts (2 misconceptions → correct with table shown); Feynman explain-back PASS (own fraud-detection example; named "prior" as the forgotten term). Highest Bloom: Apply (Bayes computation) + Analyze (why Naive Bayes probabilities are miscalibrated yet rank well).
**Implications:** unlocks Phase 1 L08 (Optimization — gradient descent) and downstream uncertainty/calibration work (confidence calibration, threshold setting, Bayesian A/B testing). Recurring failure mode is unit/rate-matching slips (multiplying the right rate by the wrong group) — re-probe those specifically in review.
