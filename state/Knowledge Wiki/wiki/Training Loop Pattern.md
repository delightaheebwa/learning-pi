<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Training Loop Pattern

The engine of every deep learning model. Every Marconi Lab model — cervical cell classifier, crop disease detector, Luganda text generator — runs on this same loop.

## The 5-Step Mantra

**Zero → Forward → Loss → Backward → Update**

```python
for X_batch, y_batch in loader:
    # 1. ZERO gradients (or they accumulate)
    optimizer.zero_grad()

    # 2. FORWARD pass: compute predictions
    outputs = model(X_batch)

    # 3. Compute LOSS
    loss = loss_fn(outputs, y_batch)

    # 4. BACKWARD pass: compute gradients
    loss.backward()

    # 5. UPDATE weights
    optimizer.step()
```

## Why Each Step Matters

| Step | What It Does | What Happens If You Skip It |
|------|-------------|------------------------------|
| `zero_grad()` | Resets gradients from previous batch | Gradients accumulate — effectively larger batch size, possible NaN |
| Forward pass | Input → layers → prediction | No prediction → no loss → nothing to learn |
| Loss | Measures prediction error | No signal to guide learning |
| `backward()` | Computes ∂loss/∂(every weight) | No gradients → weights never update |
| `step()` | Updates weights using gradients | Gradients computed but never used |

## Full Setup

```python
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

model = DiagnosticModel(n_inputs=10, n_hidden=32, n_classes=3)
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

dataset = TensorDataset(X_train, y_train)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

for epoch in range(num_epochs):
    model.train()
    for X_batch, y_batch in loader:
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = loss_fn(outputs, y_batch)
        loss.backward()
        optimizer.step()
```

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14

## Sources

- PyTorch — Optimization tutorial: https://pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- PyTorch — Training with PyTorch (YouTube series): https://pytorch.org/tutorials/beginner/introyt/trainingyt.html

## Connections
- Prerequisites: PyTorch Model Building, Loss Functions (PyTorch)
- Leads to: Evaluation Protocol, CNN Architecture Pattern, Transfer Learning (PyTorch)
