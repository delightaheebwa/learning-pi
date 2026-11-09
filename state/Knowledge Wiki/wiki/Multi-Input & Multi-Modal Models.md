<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Multi-Input & Multi-Modal Models

Real-world problems often have **multiple data sources**. Example: a cervical cancer diagnosis might combine a Pap smear **image** with patient **tabular data** (age, HPV status, previous screenings). PyTorch makes this straightforward with separate pathways that merge.

```python
class MultiModalDiagnosis(nn.Module):
    """Combines image features + tabular patient data for diagnosis."""
    def __init__(self, num_tabular_features, num_classes):
        super().__init__()
        # Image pathway
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1))
        )
        # Tabular pathway
        self.tabular_net = nn.Sequential(
            nn.Linear(num_tabular_features, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU()
        )
        # Combined classifier
        self.classifier = nn.Linear(64 + 32, num_classes)

    def forward(self, image, tabular):
        img_features = self.cnn(image).squeeze()
        tab_features = self.tabular_net(tabular)
        combined = torch.cat([img_features, tab_features], dim=1)
        return self.classifier(combined)
```

## Pattern

Multi-input models are just **multiple pathways that merge**. Each pathway extracts features from its data type, then you concatenate them and classify. PyTorch's flexibility makes this natural.

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- PyTorch docs — `torch.cat`: https://pytorch.org/docs/stable/generated/torch.cat.html
- PyTorch docs — `nn.Module`: https://pytorch.org/docs/stable/generated/torch.nn.Module.html

## Connections

- Prerequisites: CNN Architecture Pattern, Training Loop Pattern
- Relates to: LSTM (Long Short-Term Memory) — LSTMs can be one pathway in a multi-modal model
