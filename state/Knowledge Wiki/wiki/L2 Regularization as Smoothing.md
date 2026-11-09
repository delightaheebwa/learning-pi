<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# L2 Regularization as Smoothing

In the counting approach, add-1 smoothing prevents zero probabilities. In the neural approach, L2 regularization plays an analogous role — it discourages extreme weights and pushes the model toward a smoother (more uniform) distribution:

```python
reg_loss = 0.01 * (W**2).mean()
loss = negative_log_likelihood + reg_loss
```

**The mechanism:** If the weights (and biases) are driven to 0, the logits are 0 and `exp(0) = 1` for every class, so softmax produces a **uniform** distribution — the smoothest possible. The regularization strength controls how hard weights are pulled toward zero, analogous to how the number of fake counts controls smoothness in count-based models. (With nonzero biases, the logits need not be zero even when weights are zero.)

| Approach | Smoothness Mechanism | Effect on Distribution |
|---|---|---|
| Counting | Add fake counts (+1 → +k) | Pulls toward uniform |
| Neural | L2 penalty on W | Pulls toward uniform |

**Why it matters:** Smoothing/regularization prevents overconfidence — forcing the model to reserve probability mass for unseen events. In count-based models, a single unseen event can make the probability (and loss) infinite without smoothing.

Related: [[Add-1 Smoothing]] | [[Regularization Tug-of-War]]

Part of: Neural Networks: Zero to Hero — Karpathy Lecture 2 + Socratic tutoring session

## Sources

- https://cs231n.github.io/neural-networks-2/
- https://en.wikipedia.org/wiki/Regularization_(mathematics)
