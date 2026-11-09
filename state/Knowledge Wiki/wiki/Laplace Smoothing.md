<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Laplace Smoothing (Add-1 Smoothing)

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Naive Bayes]], [[Bayes' Theorem]]

## The Problem

If a word never appeared during training → zero frequency → kills the entire probability product (log(0) is undefined).

## The Fix

Add 1 count to every word-class pair:

$$P(\text{word} | \text{class}) = \frac{\text{count}(\text{word}, \text{class}) + 1}{\text{total words in class} + \text{vocabulary size}}$$

Keeps probability normalized but never zero.

## Why the Denominator Grows by Vocabulary Size

The +1 in the numerator is added to *every* word in the vocabulary — not just this one. The denominator grows by V (vocabulary size) to keep all word probabilities summing to 1. Without it, probabilities would sum to more than 1 and break the axioms.

## Worked Example

"prize" appears 3× in spam (50 total spam words), vocabulary = 200 unique words:

`P("prize"|spam) = (3 + 1) / (50 + 200) = 4/250 = 0.016`

An unseen word gets `1/250 = 0.004` — small, but not zero. That nonzero floor is the whole point.

## Why It Works

The +1 is a small correction that prevents any probability from being exactly zero, while the denominator adjustment (adding vocabulary size) keeps the distribution properly normalized.

## Sources

- https://en.wikipedia.org/wiki/Additive_smoothing
