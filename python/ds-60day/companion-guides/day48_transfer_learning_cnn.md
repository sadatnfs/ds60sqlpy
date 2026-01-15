# Day 48 — Transfer Learning with CNNs (Companion Guide)

## Learning objectives
- Load pretrained CNNs (e.g., ResNet), freeze/unfreeze layers
- Prepare image datasets with transforms and augmentation
- Fine-tune head and optionally backbone with schedulers

## Why this matters
Pretrained features drastically reduce data needs and training time for vision tasks.

## Core concepts and examples
### Data and transforms
```python
from torchvision import datasets, transforms
tr = transforms.Compose([
    transforms.Resize(256), transforms.CenterCrop(224),
    transforms.ToTensor(), transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])
train_ds = datasets.ImageFolder('data/train', transform=tr)
```

### Model and head
```python
import torchvision.models as models
import torch.nn as nn
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
for p in model.parameters(): p.requires_grad = False
model.fc = nn.Linear(model.fc.in_features, n_classes)
```

### Fine-tuning
```python
# first train head
opt = torch.optim.Adam(model.fc.parameters(), lr=1e-3)
# later unfreeze some blocks and use smaller lr
for p in model.layer4.parameters(): p.requires_grad = True
opt = torch.optim.Adam([{'params': model.fc.parameters(), 'lr':1e-3},
                        {'params': model.layer4.parameters(), 'lr':3e-4}])
```

## Common pitfalls
- Forgetting ImageNet normalization; performance collapses
- Too high LR when unfreezing leading to catastrophic forgetting
- Class imbalance; use WeightedRandomSampler or class weights

## Practice exercises
1) Train only the head; then unfreeze last block and compare
2) Add augmentation (RandomResizedCrop, Flip, ColorJitter) and measure impact
3) Use OneCycleLR and observe training dynamics

## Further reading
- Torchvision models: https://pytorch.org/vision/stable/models.html
