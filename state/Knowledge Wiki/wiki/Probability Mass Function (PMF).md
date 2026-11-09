<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Probability Mass Function (PMF)

A function $P(X = k)$ that maps each discrete outcome $k$ to its exact probability of occurring.

## Properties

- **Non-negative**: $0 \leq P(X = k) \leq 1$ for all $k$
- **Sums to one**: $\sum_k P(X = k) = 1$ — every possible outcome together accounts for all probability

## Why it matters in ML

Every classifier output is a PMF. When a neural network classifies an image, the softmax at the end converts raw logits into a valid PMF — a set of class probabilities that sum to 1. Cross-entropy loss then compares this predicted PMF against the true distribution (one-hot encoded label).

## Key insight

A PMF is just a lookup table. For a fair die: P(X=1) = 1/6, P(X=2) = 1/6, ..., P(X=6) = 1/6. The PMF doesn't tell you what will happen — it tells you the probability of each possible thing that could happen.

## Examples

- **Bernoulli distribution**: P(X=1) = p, P(X=0) = 1-p (coin flip)
- **Categorical distribution**: P(X=i) = p_i for i ∈ {1, ..., k} (multi-class)
- **Binomial distribution**: P(X=k) = C(n,k) p^k (1-p)^{n-k} (n coin flips)

## Source

- Lesson: `Teach/ai-engineering/lessons/0002-probability-foundations.html`
- https://en.wikipedia.org/wiki/Probability_mass_function
