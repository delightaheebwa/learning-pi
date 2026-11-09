<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Counts → Probabilities (Row Normalization)

## Overview
Converting raw counts into valid probability distributions by normalizing each row of the count matrix to sum to 1.

## The Operation
```
P = N.float()
P /= P.sum(1, keepdim=True)
```

Each row `i` of `N` contains counts of what character followed character `i`. Dividing by the row sum gives P(j | i) — probability of character `j` given we're at character `i`.

## The keepdim=True Trap
**Without `keepdim=True`:** `N.sum(1)` returns shape `(27,)` → PyTorch broadcasts it as `(1, 27)` (a row vector), copying it vertically across all rows. This **normalizes columns instead of rows** — every entry in column j gets divided by the sum of row j. Silent bug, no error raised for square matrices because `(27, 27) / (1, 27)` works.

**With `keepdim=True`:** shape is `(27, 1)` (column vector), copied horizontally across columns. Each row is correctly divided by its own sum.

## Why It Matters
Without correct row normalization, the model doesn't learn valid conditional probability distributions. Loss calculations downstream will be silently wrong.

## Source
Karpathy, "makemore Part 1" — Neural Networks: Zero to Hero, Lecture 2. PDF: Socratic tutoring session on broadcasting.

## Sources

- https://pytorch.org/docs/stable/generated/torch.Tensor.sum.html
- https://pytorch.org/docs/stable/notes/broadcasting.html
