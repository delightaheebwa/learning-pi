<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Softmax Function

Converts raw logits into a probability distribution. Two steps:

1. **Exponentiate:** `counts = logits.exp()` — makes everything positive
2. **Normalize:** `probs = counts / counts.sum(1, keepdim=True)` — each row sums to 1

```python
logits = xenc @ W          # (N, 27) raw scores
counts = logits.exp()       # (N, 27) positive "fake counts"
probs = counts / counts.sum(1, keepdim=True)  # (N, 27) probabilities
```

**Why exponentiate?** It ensures all "counts" are positive (any real → positive after exp), and it amplifies differences — large logits get much larger probabilities.

**Why `keepdim=True`?** Without it, broadcasting normalizes columns instead of rows — same silent bug as the count-based approach (see [[Counts-to-Probabilities (keepdim trap)]]).

In practice, `F.softmax(logits, dim=1)` does both steps in one numerically stable call. Writing it out manually reveals the structure.

Part of: Neural Networks: Zero to Hero — makemore Part 2 (Karpathy Lecture 3)

[[One-Hot Encoding]] | [[Row-Select Property]] | [[Negative Log-Likelihood (NLL)]]

## Sources

- Karpathy, "Building makemore Part 2: MLP" (Neural Networks: Zero to Hero, Lecture 3): https://www.youtube.com/watch?v=TCH_1BHY58I
- Softmax function (Wikipedia): https://en.wikipedia.org/wiki/Softmax_function
