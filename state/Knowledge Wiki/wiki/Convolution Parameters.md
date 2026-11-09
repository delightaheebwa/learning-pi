<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Convolution Parameters

The key parameters that define a Conv2d layer:

| Parameter | What It Means | Typical Value |
|-----------|---------------|---------------|
| `in_channels` | Number of input channels (3 for RGB, 1 for grayscale) | Depends on data |
| `out_channels` | How many different filters to learn | 32, 64, 128… (doubles each layer) |
| `kernel_size` | Size of the sliding window | 3 (the universal default) |
| `stride` | How many pixels to slide each step | 1 (no skipping) or 2 (downsample) |
| `padding` | Extra border pixels to preserve spatial dimensions | `kernel_size // 2` ("same" padding) |

With `padding=1` and `kernel_size=3`: output_size = (input_size + 2×1 − 3)/1 + 1 = input_size (dimensions preserved).

## Source
- **Lesson:** Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- **Date learned:** 2026-07-15

## Connections
- Prerequisites: Convolution Operation

## Sources

- https://en.wikipedia.org/wiki/Convolutional_layer
