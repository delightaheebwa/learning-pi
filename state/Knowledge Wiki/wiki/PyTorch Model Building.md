<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# PyTorch Model Building

Every neural network in PyTorch is a subclass of `nn.Module`. You define **layers** in `__init__` and data flow in `forward`.

A single layer computes: `output = activation(weights × input + bias)`

Every layer has learnable **weights** (W) and **biases** (b).

## Pattern

```python
import torch.nn as nn

class DiagnosticModel(nn.Module):
    def __init__(self, n_inputs, n_hidden, n_classes):
        super().__init__()
        self.layer1 = nn.Linear(n_inputs, n_hidden)
        self.layer2 = nn.Linear(n_hidden, n_hidden)
        self.layer3 = nn.Linear(n_hidden, n_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)  # raw logits — no activation on output
        return x
```

The output layer returns **raw logits** (no softmax) because `nn.CrossEntropyLoss()` applies softmax internally.

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14
- **Further reading:** [What is torch.nn really?](https://pytorch.org/tutorials/beginner/nn_tutorial.html)

## Connections
- Prerequisites: Tensors (PyTorch)
- Leads to: Training Loop Pattern, Activation Functions, Loss Functions (PyTorch)

## Sources (verified)

- https://pytorch.org/tutorials/beginner/nn_tutorial.html
- https://pytorch.org/docs/stable/nn.html
