<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Transfer Learning (PyTorch)

The technique you'll actually use at Marconi Lab. Instead of training a CNN from scratch (millions of images needed), take a model pre-trained on ImageNet (1.2M images) and **fine-tune** it on your small medical/agricultural dataset.

## Why It Works

Early CNN layers learn **universal visual features** — edges, textures, shapes, color patterns. These transfer across domains (cats → cervical cells → cassava leaves). Only the final layers need to adapt to your specific task.

## The Recipe

```python
from torchvision.models import resnet50, ResNet50_Weights

# 1. Load pre-trained model
model = resnet50(weights=ResNet50_Weights.DEFAULT)

# 2. Freeze all layers (keep ImageNet knowledge)
for param in model.parameters():
    param.requires_grad = False

# 3. Replace the final classification layer
model.fc = nn.Sequential(
    nn.Linear(model.fc.in_features, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, num_classes)
)

# 4. Train only the new classifier layer
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)
```

## Marconi Lab Applications

| Project | Architecture | Task |
|---------|-------------|------|
| Cervical cancer | ResNet-50 → fine-tune on Pap smears | Binary (lesion/healthy) |
| Crop disease | ResNet/EfficientNet → fine-tune on leaf photos | Multi-class |
| Tree species | ResNet → fine-tune on drone/satellite imagery | Multi-class + detection |
| Ultrasound analysis | U-Net (segmentation) | Pixel-level lesion segmentation |

The training loop from Day 1 stays the same — only the model and data change.

## Source
- **Lesson:** Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- **Date learned:** 2026-07-15
- **Further reading:** [PyTorch Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

## Sources

- PyTorch — Transfer Learning tutorial: https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- torchvision — Models: https://pytorch.org/vision/stable/models.html

## Connections
- Prerequisites: CNN Architecture Pattern, Data Augmentation (torchvision), Training Loop Pattern
