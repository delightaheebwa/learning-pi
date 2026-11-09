<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Normal_distribution ; https://en.wikipedia.org/wiki/Conjugate_prior | verified-by=fact-check-agent | date=2026-10-26 -->

# Gaussian distribution

The Gaussian distribution, also called the normal distribution, is one of the most important probability distributions in machine learning.

## Why it is useful

- It belongs to the exponential family.
- Sums of Gaussian variables are still Gaussian.
- Linear transformations of Gaussian variables are still Gaussian.
- Those closure properties make it easy to work with.

## Conjugacy

Gaussian priors and Gaussian likelihoods form a conjugate pair.

That means the posterior is also Gaussian, so Bayesian updates can often be done in closed form.

## Intuition

The Gaussian is a good default model when many small effects combine to produce a noisy quantity.

## Related pages

- [[Probability foundations]]
- [[Probability mass and density functions]]
- [[Bayes rule]]
- [[Covariance and correlation]]

## Sources

- https://en.wikipedia.org/wiki/Normal_distribution
- https://en.wikipedia.org/wiki/Conjugate_prior
