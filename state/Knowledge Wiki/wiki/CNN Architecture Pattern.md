<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# CNN Architecture Pattern

The standard CNN pattern: **Conv → ReLU → MaxPool**, repeated 2–4 times, then flattened and fed into a small fully-connected classifier.

```python
class CropDiseaseCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 256→128

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 128→64

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 64→32
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 32 * 32, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
```

**The pattern:** channels increase (3→32→64→128) while spatial dimensions decrease (256→128→64→32). The network trades spatial detail for semantic depth — going from "this is a pixel" to "this is a diseased leaf."

## Source
- **Lesson:** Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- **Date learned:** 2026-07-15

## Sources

- PyTorch `Conv2d`: https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html
- Convolutional neural network: https://en.wikipedia.org/wiki/Convolutional_neural_network

## Connections
- Prerequisites: Convolution Operation, Pooling (MaxPool2d)
- Related: Transfer Learning (PyTorch) — the pattern you'll use in practice
