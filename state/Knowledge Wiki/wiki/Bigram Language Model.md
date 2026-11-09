<!-- provenance: status=verified | source=https://www.youtube.com/watch?v=PaCmpygFfXo (Karpathy, makemore Part 1) | verified-by=fact-check-agent | date=2026-10-26 -->

# Bigram Language Model

## Overview
A **bigram** language model is the simplest possible neural/count-based language model — it predicts the next character/word using **only the immediately preceding token**. Context length = 1.

## Key Idea
- Extract every consecutive pair `(ch1, ch2)` from training data
- Count occurrences in a 2D matrix N of shape `(vocab_size, vocab_size)`
- Normalize each row to get P(next | current)
- Sample from the row distribution to generate

## Start/End Sentinels
Special character `.` marks both start and end of a sequence:
- `.E` → probability distribution over first characters
- `a.` → probability that `a` ends a word
- `..` → remains zero (no empty words)

## Limitations
- No memory beyond the last character → generates mostly unpronounceable garbage
- Cannot capture long-range dependencies (e.g. "th" context for "e" vs "a")
- But it's *learning* — generations are better than uniform random sampling

## Relation to Neural Nets
A single linear layer (no bias, no activation) with one-hot input learns the exact same 27×27 table that the counting approach computes directly. One-hot × W = W[row, :] — row selection.

## Key Insight
> "A bigram model has no memory beyond the last character — it doesn't know that 'h' as a one-character name is nonsense, it just knows 'h' sometimes ends words."
> — Karpathy

## See Also
- [[Language Model]]
- [[Counts → Probabilities (Row Normalization)]]
- [[Add-1 Smoothing]]
- [[Negative Log-Likelihood (NLL)]]
- [[Sampling from a Language Model]]

## Source
Karpathy, "makemore Part 1: The Spelled-Out Intro to Language Modeling" — Lecture 2 of Neural Networks: Zero to Hero. Part 1 only (before "Part 2: The Neural Network Approach").

## Sources
- YouTube — The spelled-out intro to language modeling: building makemore: https://www.youtube.com/watch?v=PaCmpygFfXo
