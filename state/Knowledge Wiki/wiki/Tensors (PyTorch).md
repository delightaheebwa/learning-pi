<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Tensors (PyTorch)

A **tensor** is a multi-dimensional array of numbers — the universal data container in deep learning. Images, text, audio, and tabular data all become tensors before a model processes them.

## Common Shapes by Domain

| Data Type | Shape Pattern | Lab Use |
|-----------|--------------|---------|
| Tabular | `[batch, features]` | Clinical diagnosis from lab values |
| Grayscale Image | `[batch, 1, H, W]` | Ultrasound scans |
| Color Image | `[batch, 3, H, W]` | Crop leaf photos, Pap smears |
| Sequence | `[batch, time, features]` | Temperature/weather forecasting |
| Tokenized Text | `[batch, seq_len]` | Luganda NLP |

PyTorch uses **channels-first** (NCHW) format — unlike TensorFlow's channels-last (NHWC).

## Key Operations

```python
import torch

x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
zeros = torch.zeros(2, 3)
ones = torch.ones(2, 3)
rands = torch.randn(2, 3)  # random normal, mean=0, std=1

# Attributes
x.shape   # torch.Size([2, 3])
x.dtype   # torch.float32
x.device  # cpu or cuda:0

# Device transfer
if torch.cuda.is_available():
    x = x.to('cuda')
```

`torch.randn()` is how most neural network weights start — random numbers gradually adjusted into something meaningful.

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14
- **DataCamp:** Introduction to Deep Learning with PyTorch (Ch. 1)
- **Further reading:** [PyTorch Tensor Tutorial](https://pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html)

## Sources

- PyTorch — Tensor basics tutorial: https://pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html
- PyTorch docs — torch.Tensor: https://pytorch.org/docs/stable/tensors.html

## Connections
- Leads to: PyTorch Model Building, Training Loop Pattern
