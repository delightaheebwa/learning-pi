<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Regularization Techniques

Overfitting = model memorizes training data but fails on new data. With small medical/agricultural datasets, this is the #1 enemy.

| Technique | What It Does | PyTorch |
|-----------|-------------|---------|
| **Dropout** | Randomly disables neurons during training. Forces redundancy — no single neuron can dominate. | `nn.Dropout(p=0.5)` |
| **Weight Decay (L2)** | Adds penalty for large weights. Encourages simpler models. | `optim.Adam(..., weight_decay=1e-4)` |
| **Early Stopping** | Stop training when validation loss stops improving. Prevents memorization. | Manual: track best val loss, save checkpoint |
| **Data Augmentation** | Artificially expands dataset — the best regularizer. | `torchvision.transforms` |

## Early Stopping Pattern

```python
best_val_loss = float('inf')
patience = 5
counter = 0

for epoch in range(max_epochs):
    train_loss = train_one_epoch(model, train_loader)
    val_loss = validate(model, val_loader)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_model.pt')
        counter = 0
    else:
        counter += 1
        if counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break
```

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- https://pytorch.org/docs/stable/nn.html#dropout-layers
- https://pytorch.org/docs/stable/optim.html

## Connections

- Prerequisites: Training Loop Pattern
- Relates to: Data Augmentation (torchvision)
