<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Bernoulli_distribution | verified-by=fact-check-agent | date=2026-10-26 -->

# Bernoulli Distribution

The simplest probability distribution: one trial with exactly two outcomes (success/failure, 1/0).

## Definition

$$P(X = k) = p^k (1-p)^{1-k}, \quad k \in \{0, 1\}$$

- $p$ = probability of success (X=1)
- $1-p$ = probability of failure (X=0)

## Key statistics

- **Mean (expected value)**: $E[X] = p$
- **Variance**: $Var(X) = p(1-p)$

## Why it matters in ML

Binary classification is Bernoulli. When you build a model that predicts "spam" vs "not spam", or "cat" vs "dog", the model outputs a single number p — the probability of the positive class. The negative class probability is just 1-p.

The Bernoulli distribution also forms the building block for:
- **Binomial**: n independent Bernoulli trials
- **Multi-label classification**: multiple independent Bernoulli outputs

## Implementation insight

A Bernoulli sampler is trivial: generate a uniform random number u ∈ [0, 1], return 1 if u < p, else 0. This is inverse transform sampling in its simplest form.

## Source

- Lesson: `Teach/ai-engineering/lessons/0002-probability-foundations.html`

## Sources
- Wikipedia — Bernoulli distribution: https://en.wikipedia.org/wiki/Bernoulli_distribution
