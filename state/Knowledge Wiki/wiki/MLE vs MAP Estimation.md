<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# MLE vs MAP Estimation

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Bayes' Theorem]], [[Prior Probability]], [[Laplace Smoothing]], [[Conjugate Priors]]

## MLE — Maximum Likelihood Estimation

Chooses the parameters that maximize P(data|parameters): "what parameters make the data I saw most likely?" For discrete counts this reduces to relative frequency — just counting. No prior; with small data it overfits (memorizes instead of generalizing).

## MAP — Maximum A Posteriori

Chooses the parameters that maximize P(parameters|data). By Bayes' theorem:

`P(parameters|data) ∝ P(data|parameters) · P(parameters)`

MAP adds a prior over the parameters themselves — a belief about what values are plausible before seeing data.

## The Regularization Connection

| Estimation | Optimizes | ML equivalent |
|------------|-----------|---------------|
| MLE | P(data\|params) | Unregularized training |
| MAP | P(data\|params)·P(params) | L2 / L1 regularization |

A **Gaussian** prior on weights = L2 (ridge) regularization. A **Laplace** prior = L1 (lasso). Every regularization term is a Bayesian statement: `weight_decay` in Adam, `C` in a linear SVM, `alpha` in ridge regression — all priors in disguise.

## Worked Example

10 coin flips, 7 heads. MLE bias = 7/10 = **0.7** (data speaks alone). MAP with a Beta(2,2) prior ("coins are roughly fair") = (7+2−1)/(10+2+2−2) = 8/12 ≈ **0.667** — the prior pulls the estimate back toward 0.5.

## When the Prior Matters Most

With scarce data (few-shot learning, cold start) the prior carries the signal. With massive data the likelihood overwhelms any prior and MLE ≈ MAP — which is why large-scale training is effectively frequentist.

## Sources

- Wikipedia — Maximum likelihood estimation: https://en.wikipedia.org/wiki/Maximum_likelihood_estimation
- Wikipedia — Maximum a posteriori estimation: https://en.wikipedia.org/wiki/Maximum_a_posteriori_estimation
- Stanford MS&E 226 — Beta-binomial MAP (mode): http://web.stanford.edu/~rjohari/teaching/notes/226_lecture16_inference.pdf
