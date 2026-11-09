# Review — Random variable — 2026-05-21

**Concept:** Random variable  
**Status after review:** developing  
**Next review:** 2026-05-24 (3 days)

## Question Asked

Formally, a random variable is a function — what does it map from and to? And what does this mapping enable that you couldn't do with the raw sample space alone?

## Answer Given

User correctly identified: maps from raw outcome/sample space to a target space, turning outcomes into numbers that are easier to work with for ML tasks.

## Evaluation

Partially correct. The mapping intuition and practical motivation are solid, but two key pieces are missing:

1. **Formal precision**: X: Ω → S is a *measurable* function, where Ω is the sample space and S is typically ℝ or ℝⁿ.
2. **Pushforward measure**: P_X(B) = P(X⁻¹(B)) — this is the mechanism that transfers probability from the sample space to the numerical target space. Without it, there's no formal justification for why the random variable inherits a probability distribution.

## Correct Answer

A random variable X: Ω → S is a measurable function from the sample space Ω to a target space S (usually ℝ). Its probability distribution is the pushforward measure: P_X(B) = P(X⁻¹(B)) — the probability that X lands in set B equals the probability (in the original space) of all outcomes that X maps into B. This lets us work with P(X ≥ 5) or E[X] without ever touching the raw sample space.

## Notes

User's intuition is developing well — they understand the "why" (practical utility for ML). The next step is internalizing the pushforward as the formal "how" that makes random variables mathematically rigorous.
