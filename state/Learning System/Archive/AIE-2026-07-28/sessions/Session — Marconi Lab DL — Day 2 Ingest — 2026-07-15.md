# Session — Marconi Lab DL — Day 2 Ingest

- **Date:** 2026-07-15
- **Topic:** Marconi Lab Deep Learning — Day 2: CNNs for Medical & Agricultural Images
- **Source:** Marconi Lab DL Course, Day 2 (HTML lesson)
- **Type:** Ingest

## Concepts Ingested

| Concept | Status | Next Review | Wiki |
|---|---|---|---|
| Convolution Operation | developing | 2026-07-18 | [[Convolution Operation]] |
| Convolution Parameters | developing | 2026-07-19 | [[Convolution Parameters]] |
| Pooling (MaxPool2d) | developing | 2026-07-20 | [[Pooling (MaxPool2d)]] |
| CNN Architecture Pattern | developing | 2026-07-18 | [[CNN Architecture Pattern]] |
| Data Augmentation (torchvision) | developing | 2026-07-19 | [[Data Augmentation (torchvision)]] |
| Transfer Learning (PyTorch) | developing | 2026-07-20 | [[Transfer Learning (PyTorch)]] |

## Summary

Ingested the Marconi Lab DL Day 2 lesson covering CNNs for image classification. Key takeaways:

- CNNs solve two fatal problems of fully-connected nets for images: excessive parameters and no spatial awareness
- Convolution = small sliding filters (kernels) producing feature maps; Conv2d parameters: in/out_channels, kernel_size (default 3), stride, padding
- Standard pattern: Conv → ReLU → MaxPool repeated, then Flatten → FC classifier (channels increase, spatial dims decrease)
- Data augmentation expands small medical/ag datasets (NEVER on test data)
- Transfer learning is the real technique used at Marconi Lab: freeze pre-trained early layers, replace classifier head, fine-tune
- The training loop NEVER changes — identical to Day 1's Zero → Forward → Loss → Backward → Update pattern
