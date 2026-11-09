<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Data Augmentation (torchvision)

Medical and agricultural datasets are typically **small** (e.g., 200 cervical cell images). Data augmentation artificially expands your dataset by applying random but realistic transformations.

```python
from torchvision import transforms

train_transforms = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Test: NO augmentation — only normalize!
test_transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])
```

## Critical Rule

**Never** apply augmentation to test/validation data. Augmentation is for training only. The test set must represent real, unmodified images that the model would encounter in production.

The ImageNet normalization stats (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`) are the standard for pre-trained models and should be used with transfer learning.

## Source
- **Lesson:** Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- **Date learned:** 2026-07-15
- **Further reading:** [torchvision.transforms docs](https://pytorch.org/vision/stable/transforms.html)

## Connections
- Prerequisites: CNN Architecture Pattern
- Leads to: Transfer Learning (PyTorch)
