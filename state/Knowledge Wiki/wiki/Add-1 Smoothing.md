<!-- provenance: status=verified | source=https://github.com/karpathy/nn-zero-to-hero/blob/master/lectures/makemore/makemore_part1_bigrams.ipynb ; https://github.com/karpathy/makemore/blob/master/names.txt | verified-by=fact-check-agent | date=2026-10-26 -->

# Add-1 Smoothing

## Overview
**Add-1 (Laplace) smoothing** adds a small fake count to every possible bigram entry, ensuring no entry is ever zero. This prevents log(0) = −∞ from breaking the loss function.

## Why It's Needed
- Many bigrams never appear in training (e.g. `j → q` in English names)
- Without smoothing, the model assigns P = 0 to unseen bigrams
- NLL loss computes −ln(P) → −ln(0) = +∞ → the average loss becomes **+∞ (inf)**, so gradients are unusable/NaN downstream (PyTorch reports `inf`, not `NaN`, when only the log term is infinite)

## Implementation
```python
P = (N + 1).float()
P /= P.sum(1, keepdim=True)
```

This is the count-model analogue of L2 regularization / weight decay in the neural-network version: both push predictions away from over-confidence toward a more uniform distribution. They are **not literally equivalent** — the +1 prior acts on counts directly, L2 acts on weights via the loss.

## Effect
- Every bigram gets a tiny non-zero probability. For Karpathy's `names.txt` (32,033 names), `j → q` has count 0 and row total 2900, so smoothed P = 1/(2900+27) ≈ 0.000342
- −ln(0.000342) ≈ 7.98 instead of ∞
- The loss remains finite and trainable

## Trade-off
Higher smoothing → more uniform distribution → lower confidence on seen patterns. Use dev set to tune the smoothing strength (the fake count value).

## Source
Karpathy, "makemore Part 1" — Neural Networks: Zero to Hero, Lecture 2.

## Sources

- Lecture 2 notebook (smoothing cell, `P = (N + 1).float()`): https://github.com/karpathy/nn-zero-to-hero/blob/master/lectures/makemore/makemore_part1_bigrams.ipynb
- `names.txt` dataset used in the lecture: https://github.com/karpathy/makemore/blob/master/names.txt
- Laplace/additive smoothing background: https://en.wikipedia.org/wiki/Additive_smoothing ; Jurafsky & Martin SLP3 ch. 3: https://web.stanford.edu/~jurafsky/slp3/3.pdf
- Numbers above recomputed from `names.txt` with the lecture code (2026-10-26).

**Corrections (2026-10-26):** (1) an infinite NLL makes the mean loss `inf`, not `NaN`; (2) the old illustrative values (P≈0.00003, −ln≈10.4) do not match the lecture dataset — corrected to the reproducible 0.000342 / 7.98; (3) "+1 is equivalent to L2 regularization" overstated it — it is the count-model analogue.
