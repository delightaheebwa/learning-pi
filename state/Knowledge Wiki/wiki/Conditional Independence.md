<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Conditional Independence

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Naive Bayes]], [[Bayes' Theorem]]

## Definition

Two features are conditionally independent given a class if knowing one feature tells you nothing about the other, once the class is known.

## In Naive Bayes

The "naive" assumption: given the class label, every feature is independent of every other feature. For spam detection: once you know it's spam, knowing "free" appeared tells you nothing extra about whether "money" appeared.

## Practical Note

This assumption is usually false in real data, but Naive Bayes classifiers still perform well because they only need to **rank** classes correctly, not output calibrated probabilities.
## Sources

- https://en.wikipedia.org/wiki/Conditional_independence
- https://en.wikipedia.org/wiki/Naive_Bayes_classifier
