# Session — Random Variable Pre-image and Distribution — 2026-05-19

## Overview

- **Date:** 2026-05-19
- **Topic:** Random variable — pre-image, distribution, and ML motivation
- **Type:** Ingest (content from Perplexity walkthrough on MML section 6)

## Prerequisites Reviewed

None — this was an ingest, not a review session.

## New Concepts

### Pre-image of a random variable (developing)

**Definition:** X^{-1}(S) = {ω ∈ Ω : X(ω) ∈ S} — the set of all outcomes whose X-value falls in S. Lives in Ω, not T.

**Prerequisites:** Random variable
**Next review:** 2026-05-22

### Distribution of a random variable (P_X) (developing)

**Definition:** P_X(S) = P(X^{-1}(S)) — the function S ↦ P_X(S) that gives the probability X lands in S. The original measure "pushed through" X.

**Prerequisites:** Random variable; Pre-image of a random variable
**Next review:** 2026-05-22

## What Was Covered

- The fundamental identity P_X(S) = P(X^{-1}(S)) (equation 6.8) — the bridge between probabilities on T and probabilities on Ω
- Concrete two-coin example: X = number of heads, computing pre-images and probabilities for S = {0}, {1}, {2}
- Target space classification: discrete (T finite/countable) vs continuous (T = R or R^D)
- ML motivation: random variables extract numeric quantities from complex Ω into simple T where calculus works
- Cat-vs-dog classifier as a concrete ML example of Ω, T, X, and P_X

## Existing Concept Enriched

**Random variable** was already in the KB with next review 2026-05-21. The wiki page was updated to include:

- Pre-image definition
- Target space discrete vs continuous classification
- ML motivation section with cat-vs-dog example
- Cross-link to the new Distribution page

## Final Concept Statuses

| Concept | Status | Next Review |
| --- | --- | --- |
| Random variable | developing | 2026-05-21 |
| Pre-image of a random variable | developing | 2026-05-22 |
| Distribution of a random variable (P_X) | developing | 2026-05-22 |

## Open Questions

None new — existing open questions remain unchanged.