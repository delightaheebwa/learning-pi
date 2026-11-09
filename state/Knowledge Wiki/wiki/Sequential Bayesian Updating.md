<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Sequential Bayesian Updating

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Conjugate Priors]], [[Bayes' Theorem]], [[Posterior Probability]], [[Bayesian A-B Testing]]

## Today's Posterior Becomes Tomorrow's Prior

Because a conjugate posterior stays in the same family as the prior, it slots straight back in as the next prior. Systems learn incrementally without reprocessing history.

## Coin Example

- **Day 1:** Beta(1,1) — uniform, mean 0.5. No data.
- **Day 2:** 7 heads, 3 tails → Beta(8,4), mean 8/12 ≈ 0.667. Looks heads-biased.
- **Day 3:** 5 more heads, 5 more tails → Beta(13,9), mean 13/22 ≈ 0.591. Balanced data pulls back toward 0.5.

## Order Invariance

Updating with all 12 heads and 8 tails at once gives Beta(13,9) — identical to the sequential path. Batch and sequential are mathematically equivalent; sequential lets you decide at each step without storing raw data.

## Why It Matters

The foundation of online learning in production: Thompson sampling for bandits, incremental recommenders, streaming anomaly detectors — all use this pattern.

## Sources

- Conjugate prior (Wikipedia): https://en.wikipedia.org/wiki/Conjugate_prior
- Beta distribution (Wikipedia): https://en.wikipedia.org/wiki/Beta_distribution
- Bayesian updating (Wikipedia): https://en.wikipedia.org/wiki/Bayesian_inference
