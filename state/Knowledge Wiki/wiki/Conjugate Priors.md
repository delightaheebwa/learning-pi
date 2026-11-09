<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Conjugate Priors (Beta-Binomial)

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Bayes' Theorem]], [[MLE vs MAP Estimation]], [[Sequential Bayesian Updating]], [[Bayesian A-B Testing]]

## The Idea

A prior is **conjugate** when prior and posterior belong to the same distribution family. The update becomes algebraically trivial — no integrals, no sampling.

## Beta-Binomial Conjugacy

```
Prior:     Beta(a, b)
Data:      s successes, f failures
Posterior: Beta(a + s, b + f)
```

Beta(a,b) is the natural distribution for a probability parameter (a number between 0 and 1): bounded on [0,1] and flexible enough to represent any belief. Mean = a/(a+b). The sum a+b is your effective sample size — how much weight the prior carries: Beta(1,1) gives a+b=2 (low confidence, wide spread across [0,1]); Beta(100,100) gives a+b=200 (high confidence, narrow peak tightly concentrated at 0.5).

| Prior | Shape | Meaning |
|-------|-------|---------|
| Beta(1,1) | Uniform | No opinion (mean 0.5) |
| Beta(10,10) | Peaked at 0.5 | Strong belief parameter is near 0.5 |
| Beta(1,10) | Skewed toward 0 | Believe the parameter is small |

## The Conjugate Family

| Likelihood | Conjugate prior | Posterior | Example |
|-----------|----------------|-----------|---------|
| Bernoulli/Binomial | Beta(a,b) | Beta(a+s, b+f) | Coin bias, click-through rate |
| Normal (known variance) | Normal | Normal (weighted mean, smaller variance) | Sensor calibration |
| Poisson | Gamma(a,b) | Gamma(a+Σcounts, b+n) | Arrival rates |
| Multinomial | Dirichlet(α) | Dirichlet(α+counts) | Topic modeling, language models |

Without conjugacy you need MCMC sampling or variational inference to approximate the posterior. With conjugacy you update two numbers.

## Sources

- https://en.wikipedia.org/wiki/Conjugate_prior
