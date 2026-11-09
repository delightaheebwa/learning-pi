<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Convolution Operation

A **convolution** slides a small filter (kernel) across the image. At each position, it multiplies the filter values by the overlapping image pixels and sums them up. The result is a **feature map** — a new image where bright spots show where the filter detected its pattern.

*(Note: deep-learning frameworks actually compute cross-correlation — the kernel is not flipped — but because the kernel is learned, this is conventionally called "convolution".)*

CNNs solve two fatal problems with fully-connected networks on images:
1. **Too many parameters** — a 256×256×3 image → 196,608 inputs → 196M params for one hidden layer
2. **No spatial awareness** — a pixel shifted one position is treated as a completely different feature

```python
import torch.nn as nn

conv = nn.Conv2d(
    in_channels=3,      # RGB → 3 input channels
    out_channels=16,    # 16 different filters
    kernel_size=3,      # each filter is 3×3
    stride=1,           # slide 1 pixel at a time
    padding=1           # preserve spatial size
)
```

Each filter learns to detect a different pattern (edges, textures, blobs). Early layers detect low-level features; deeper layers detect higher-level patterns (cell morphology, lesion shapes).

## Source
- **Lesson:** Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- **Date learned:** 2026-07-15
- **Further reading:** [DataCamp CNN Tutorial](https://www.datacamp.com/tutorial/pytorch-cnn-tutorial)

## Connections
- Prerequisites: Tensors (PyTorch), PyTorch Model Building
- Leads to: Convolution Parameters, Pooling (MaxPool2d), CNN Architecture Pattern

## Sources

- https://en.wikipedia.org/wiki/Convolutional_neural_network
- https://en.wikipedia.org/wiki/Convolutional_layer
