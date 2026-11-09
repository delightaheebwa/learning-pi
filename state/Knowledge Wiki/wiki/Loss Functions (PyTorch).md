<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Loss Functions (PyTorch)

A **loss function** measures how far the model's predictions are from ground truth. Training minimizes this number.

## Common Losses

| Task | Loss | PyTorch Class | Lab Example |
|------|------|---------------|-------------|
| Binary classification | Binary Cross-Entropy | `nn.BCEWithLogitsLoss()` | Disease: yes/no |
| Multi-class (C classes) | Cross-Entropy | `nn.CrossEntropyLoss()` | Crop disease: 5 types |
| Regression | Mean Squared Error | `nn.MSELoss()` | Predicting temperature |

## Common Pitfall

`nn.CrossEntropyLoss()` expects **raw logits** (no softmax) — it applies softmax internally. If you apply softmax in `forward()` and also use `CrossEntropyLoss`, you're applying softmax twice and the model won't learn properly.

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14
- https://pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html
- https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
- https://pytorch.org/docs/stable/generated/torch.nn.MSELoss.html

## Connections
- Prerequisites: PyTorch Model Building
- Leads to: Training Loop Pattern
