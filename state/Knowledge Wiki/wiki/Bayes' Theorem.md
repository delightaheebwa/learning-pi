<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Bayes%27_theorem | verified-by=fact-check-agent | date=2026-10-26 -->

# Bayes' Theorem

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Phase:** 1 · Math Foundations
> **Related:** [[Prior Probability]], [[Posterior Probability]], [[Likelihood]], [[Base Rate Fallacy]], [[Naive Bayes]], [[Laplace Smoothing]], [[MLE vs MAP Estimation]], [[Conjugate Priors]], [[Bayesian A-B Testing]]

## Core Formula

$$P(H|E) = \frac{P(E|H) \cdot P(H)}{P(E)}$$

**Components:**
- **Prior P(H):** Your belief before seeing any evidence — the base rate.
- **Likelihood P(E|H):** How probable the evidence is if the hypothesis is true.
- **Evidence P(E):** Total probability of seeing E under all possibilities (Law of Total Probability):
  - `P(E) = P(E|H)·P(H) + P(E|¬H)·P(¬H)`
- **Posterior P(H|E):** Belief after incorporating evidence.

## Derivation (from Conditional Probability)

Conditional probability: `P(A|B) = P(A∩B)/P(B)`, and symmetrically `P(B|A) = P(A∩B)/P(A)`. Both expressions share the same numerator — P(A∩B). Set them equal and isolate P(A|B):

`P(A|B)·P(B) = P(B|A)·P(A)` → `P(A|B) = P(B|A)·P(A)/P(B)`

That is Bayes' theorem. No independence assumption is needed — the derivation only equates two expressions for the same joint probability.

## Why It Matters for AI/ML

AI models (ML, deep learning) work on probabilities. Bayes' Theorem is the mathematical framework for how an AI system incorporates new evidence to refine its confidence over time. Start with a belief, see evidence, update.

Without understanding this, you'll misinterpret model outputs, set bad thresholds, and ship overconfident predictions.

## Intuitive Example (Librarian/Farmer)

"Steve is meek and shy — is he a librarian or farmer?" Use the prior (how many librarians vs farmers exist), the likelihood (what proportion of each group fits the description), and compute the posterior.

## Disease Test Example

A disease affects 1 in 1000 people. A test is 99% sensitive, 1% false positive rate.

- P(disease) = 0.001 (prior / base rate)
- P(positive|disease) = 0.99 (likelihood)
- P(positive|healthy) = 0.01 (false positive rate)
- P(positive) = 0.99×0.001 + 0.01×0.999 = 0.01098
- P(disease|positive) = (0.99×0.001) / 0.01098 ≈ **9%**

**Intuitive:** In a group of 1000 people, 1 is sick (caught by test) and ~10 healthy people false-positive → 11 positive results, only 1 truly sick → ~1/11 ≈ 9%.

## Key Insight

The prior dominates when a condition is rare — even accurate tests produce mostly false positives.

## Sources
- Wikipedia — Bayes' theorem: https://en.wikipedia.org/wiki/Bayes%27_theorem

## The Forgotten Term

When someone says "the test is 99% accurate, so a positive means you're 99% sure," the single word for what they're forgetting is **prior**. Test accuracy is only the likelihood — one number, meaningless without the other (how rare the condition is). Bayes' theorem forces both into the computation. See [[Base Rate Fallacy]].
