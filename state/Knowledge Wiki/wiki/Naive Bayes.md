<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Naive Bayes Classifier

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Bayes' Theorem]], [[Laplace Smoothing]], [[Conditional Independence]], [[MLE vs MAP Estimation]]

## Formula

$$P(\text{class} | f_1, f_2, \dots, f_n) = P(\text{class}) \cdot P(f_1 | \text{class}) \cdot P(f_2 | \text{class}) \dots P(f_n | \text{class}) / P(\text{features})$$

Multiply the likelihoods of all features together. Since the denominator is the same for every class, compare numerators only (argmax over classes).

## The "Naive" Part

Naive Bayes assumes every word/feature is **conditionally independent** given the class — meaning once you know it's spam, knowing "free" appeared tells you nothing extra about whether "money" appeared.

## Why It Still Works

Despite this false assumption, Naive Bayes still works because the classifier only needs to **rank classes correctly**, not produce calibrated probabilities.

## Calibration vs Ranking

The independence assumption makes Naive Bayes **overconfident**: correlated words ("free" + "money") are treated as independent evidence, so their effects multiply and push probabilities toward 0 or 1. An output of P(spam) = 0.999 might really be ≈ 0.8.

Rule: use Naive Bayes when you only need to **rank** (spam vs ham). Do NOT trust its probabilities for calibrated thresholds — medical diagnosis, credit risk, insurance pricing, or any cost-sensitive decision.

## Variants

- **Multinomial Naive Bayes:** for text classification (word counts)
- **Gaussian Naive Bayes:** for continuous features
- **Bernoulli Naive Bayes:** for binary features

## Zero Frequency Problem

If a word never appeared during training → zero frequency → kills the entire product / log(0) undefined. Fix: [[Laplace Smoothing]].

## Log-Space Computation

Multiplying ~200 word probabilities (~0.01 each) underflows floating point (0.01^200 = 10^-400 rounds to 0). Summing log-probabilities is numerically stable and mathematically equivalent: `score(class) = log P(class) + Σ log P(word|class)`.

## From Scratch → Production

The ~40-line from-scratch class (whitespace tokenize → Laplace-smoothed counts → log-space argmax) computes the same thing as sklearn: `CountVectorizer` handles tokenization and vocabulary building; `MultinomialNB` handles smoothing and log-probabilities internally.

## Sources

- Wikipedia — Naive Bayes classifier: https://en.wikipedia.org/wiki/Naive_Bayes_classifier
- scikit-learn — Naive Bayes: https://scikit-learn.org/stable/modules/naive_bayes.html
