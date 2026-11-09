<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Pooling (MaxPool2d)

After a convolution, **pooling** downsamples the feature map. **Max Pooling** slides a 2×2 window and keeps only the maximum value in each window.

```python
pool = nn.MaxPool2d(kernel_size=2, stride=2)
# [batch, channels, H, W] → [batch, channels, H/2, W/2]
```

Only height and width change — channel count stays the same.

## Three Purposes

1. **Reduces parameters** for the final classifier layers
2. **Translation invariance** — a lesion shifted slightly produces the same pooled output
3. **Increases receptive field** — each pixel in deeper layers "sees" more of the original image

## Source
- **Lesson:** Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- **Date learned:** 2026-07-15
- PyTorch `torch.nn.MaxPool2d` — https://pytorch.org/docs/stable/generated/torch.nn.MaxPool2d.html

## Connections
- Prerequisites: Convolution Operation
- Leads to: CNN Architecture Pattern
