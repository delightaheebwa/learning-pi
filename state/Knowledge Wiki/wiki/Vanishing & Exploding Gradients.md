<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Vanishing & Exploding Gradients

During backpropagation, gradients flow backward through every layer. With sigmoid/tanh activations, each layer multiplies the gradient by a number ≤ 1 — after 10+ layers the gradient at the input is essentially zero **(vanishing)**. The opposite: large weight values compound multiplicatively, gradients become huge, and loss goes to NaN **(exploding)**.

## Standard Fixes

| Problem | Solution | How It Works |
|---------|----------|-------------|
| Vanishing | **ReLU activation** | Gradient is 0 or 1 — no squashing. Default for hidden layers. |
| Vanishing | **Batch Normalization** | Normalizes layer outputs to mean=0, std=1. Keeps gradients in healthy range. |
| Vanishing/exploding | **Proper weight init** | Kaiming (for ReLU) or Xavier (for tanh) scales weights correctly. |
| Exploding | **Gradient Clipping** | Cap gradients at max_norm. `clip_grad_norm_(model.parameters(), max_norm=1.0)` |
| Exploding | **Lower learning rate** | Smaller steps = less chance of overshooting into instability. |

```python
# Safe training setup
import torch
import torch.nn as nn
import torch.nn.init as init

class WellBehavedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(100, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.fc3 = nn.Linear(128, 10)

        init.kaiming_normal_(self.fc1.weight, mode='fan_in', nonlinearity='relu')
        init.kaiming_normal_(self.fc2.weight, mode='fan_in', nonlinearity='relu')
        init.xavier_normal_(self.fc3.weight)

    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.fc3(x)
        return x
```

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- **Further reading:** [Goodfellow §8.2.5](https://www.deeplearningbook.org/contents/optimization.html)
- https://www.deeplearningbook.org/contents/optimization.html
- https://pytorch.org/docs/stable/nn.html#torch.nn.utils.clip_grad_norm_

## Connections

- Prerequisites: Training Loop Pattern, Backpropagation
- Leads to: Optimizers (SGD, Adam, AdamW), Regularization Techniques
