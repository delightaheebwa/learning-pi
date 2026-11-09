<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Base_rate_fallacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Base Rate Fallacy

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Bayes' Theorem]], [[Prior Probability]], [[Posterior Probability]]

## Definition

The mistake of focusing on new evidence (a test result or description) while ignoring how common or rare the event actually is in reality.

## Example

A 99% accurate disease test on a 1/1000 prevalence disease → P(disease|positive) ≈ 9%, not 99%. People intuitively focus on the test accuracy (99%) and ignore the base rate (0.1%).

## Why It Matters for AI/ML

- Misinterpreting model outputs by ignoring class imbalance
- Setting bad confidence thresholds
- Shipping overconfident predictions on rare events

## The Fix

Always account for the prior. Bayes' Theorem forces you to incorporate base rates into your reasoning.

## Sources
- Wikipedia — Base rate fallacy: https://en.wikipedia.org/wiki/Base_rate_fallacy

## The 3-Step Method (concrete population)

For any base-rate problem: (1) pick a round population (e.g. 100); (2) segment by the prior — split into target/non-target groups at the prior rate; (3) count how many in each group show the evidence (group size × evidence rate). Posterior = (evidence in target group) / (total evidence).

## Worked Example: Library Cards

A town is 60% adults, 40% children; 30% of adults and 10% of children hold a library card. Out of 100 people: 60 adults → 0.30 × 60 = 18 cardholders; 40 children → 0.10 × 40 = 4 cardholders. Total cardholders = 22. P(child|card) = 4/22 ≈ 0.18 — the prior (few children) dominates the evidence.