<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Row-Select Property

When you multiply a one-hot vector by a matrix `W`, the result is just the corresponding row of `W`:

```python
xenc @ W  →  W[ix, :]  # plucks out the ix-th row
```

So logits for input "m" (index 13) = `W[13]`. After softmax, this is the probability distribution for the next character.

**What this means:** The neural bigram model with a single linear layer (no bias, no hidden layer) learns the same 27×27 table as the counting approach — just as log-probabilities instead of counts:

```python
# Counting approach:
P = N.float() / N.sum(1, keepdim=True)

# Neural approach (after training):
P_nn = W.exp() / W.exp().sum(1, keepdim=True)
# They converge to the same values
```

This bridges the two approaches. The neural framework isn't doing anything fundamentally different for the bigram case — it's learning the same table iteratively via gradient descent. The power is that the same framework extends to hidden layers, which the counting approach can't do.

Part of: Neural Networks: Zero to Hero — makemore Part 2 (Karpathy Lecture 2)

[[One-Hot Encoding]] | [[Softmax Function]] | [[Bigram Language Model]]

## Sources (verified)

- https://github.com/karpathy/makemore
