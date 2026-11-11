# Review — Sequential Bayesian Updating

> **Date:** 2026-09-09
> **Concept:** Sequential Bayesian Updating
> **Type:** concept · **Track:** aiefs
> **Overdue by:** 1 day (next_review was 2026-09-08)
> **Result:** PASS ✅
> **Question (discriminative):** A robot updates its belief about a coin's bias each day using a Beta prior. Day 1: prior is Beta(1,1), it observes 7 heads and 3 tails. Day 2: it observes 5 more heads and 5 more tails. What are the parameters of the posterior at the end of Day 2?
> **Answer:** B — Beta(13, 9) — today's posterior becomes tomorrow's prior, so you add Day 2 data to Day 1's posterior
> **Grade audit:** ✅ Gate confirmed pass
> **Mastery:** 0.50 · **Feynman:** — (not yet attempted)
> **Next review:** 2026-09-15
> **Interleaving:** discriminative (previous was definitional)

## Key Insight
Beta(1,1) → +7H,3T → Beta(8,4) → +5H,5T → Beta(13,9). Conjugate posterior slots back in as next prior — no raw data storage. Foundation of online learning (Thompson sampling, streaming anomaly detectors, incremental recommenders).
