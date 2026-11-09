<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Negative Log-Likelihood (NLL)

## Overview
The standard loss function for language models: **-ln(P(correct next token))**. Measures how surprised the model is by the actual data.

## Formula
For a single prediction: `loss = -ln(P(x))`

- P(x) = 1.0 (perfect): loss = 0
- P(x) = 0.5: loss = 0.69
- P(x) = 0.01: loss = 4.60
- P(x) → 0: loss → +∞

Averaged across all N examples in the dataset:
```
Total Loss = (1/N) × Σ -ln(P(x_i))
```

## Why Negative Log?
- Log turns multiplication of probabilities into addition (numerically stable)
- Maximizing the product of probabilities (likelihood) = minimizing the average negative log probability
- Models with lower NLL are better — they assign higher probability to the actual data

## The Zero Problem
If any example gets P(x) = 0, its loss is +∞, which makes the entire average +∞ regardless of all other predictions. This is why **model smoothing** (add-1) or equivalent is essential.

## Source
Karpathy, "makemore Part 1" — Neural Networks: Zero to Hero, Lecture 2. PDF: Socratic tutoring session on log(0) explosion.

## Sources

- Wikipedia — Likelihood function: https://en.wikipedia.org/wiki/Likelihood_function
- Karpathy, makemore Part 1 (YouTube): https://www.youtube.com/watch?v=PaCmpygFfXo
