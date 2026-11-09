<!-- provenance: status=verified | source=https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval ; https://pytorch.org/docs/stable/generated/torch.no_grad.html | verified-by=fact-check-agent | date=2026-10-26 -->

# Evaluation Protocol

Training loss going down doesn't prove your model works. You must evaluate on data the model has never seen (validation/test set).

## The Pattern

```python
model.eval()  # disables dropout, batch norm
correct = 0
total = 0

with torch.no_grad():  # no gradient tracking → faster, less memory
    for X_batch, y_batch in test_loader:
        outputs = model(X_batch)
        _, predicted = torch.max(outputs, 1)  # highest-score class
        total += y_batch.size(0)
        correct += (predicted == y_batch).sum().item()

print(f"Accuracy: {100 * correct / total:.1f}%")
```

## Critical Rules

1. **Always call `model.eval()`** before evaluation — it disables dropout and batch norm's training behavior. Forgetting gives misleadingly bad results (dropout randomly disables neurons during inference).
2. **Wrap in `torch.no_grad()`** — disables gradient tracking, saving memory and computation. Without it, autograd builds a graph and tracks gradients you'll never use.
3. `model.eval()` switches layers to inference mode; `torch.no_grad()` disables gradient tracking — they work together but do different things.

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14

## Connections
- Prerequisites: Training Loop Pattern

## Sources

- https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval
- https://pytorch.org/docs/stable/generated/torch.no_grad.html
