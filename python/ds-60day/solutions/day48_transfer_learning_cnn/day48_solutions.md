# Day 48 — Solutions: Transfer Learning with CNNs

We fine-tune a pretrained ResNet on an ImageFolder dataset. We first train a linear head, then unfreeze the last block. We also add data augmentation and use OneCycleLR. Each block is followed by a step‑by‑step explanation.

Contents
- Exercise 1: Train only the head; then unfreeze last block and compare
- Exercise 2: Add augmentation and measure impact
- Exercise 3: Use OneCycleLR and observe training dynamics

---

Setup and dataset
```python
# 1) Imports
import torch, torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 2) Reproducibility and device
torch.manual_seed(0)
np.random.seed(0)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 3) Paths
root = Path('data')
train_dir = root/'train'
valid_dir = root/'valid'

# 4) Transforms (ImageNet normalization)
mean, std = [0.485,0.456,0.406], [0.229,0.224,0.225]
val_tfms = transforms.Compose([
    transforms.Resize(256), transforms.CenterCrop(224),
    transforms.ToTensor(), transforms.Normalize(mean, std)
])

# 5) Datasets and loaders
train_ds = datasets.ImageFolder(train_dir, transform=val_tfms)
valid_ds = datasets.ImageFolder(valid_dir, transform=val_tfms)
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True, num_workers=0)
valid_dl = DataLoader(valid_ds, batch_size=128, num_workers=0)

n_classes = len(train_ds.classes)
```
Explanation
- transforms: Always normalize to ImageNet stats for pretrained ImageNet weights
- ImageFolder: expects subfolders per class under train/ and valid/
- DataLoader: `num_workers=0` is portable in notebooks and on Windows. Increase
  it only after moving loader creation under a script's `if __name__ ==
  "__main__":` guard and measuring a benefit.

---

Exercise 1 — Linear head then unfreeze last block
```python
# 1) Load pretrained model
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
# 2) Freeze backbone
for p in model.parameters():
    p.requires_grad = False
# 3) Replace head
model.fc = nn.Linear(model.fc.in_features, n_classes)
model = model.to(device)

# 4) Train head only
opt = torch.optim.Adam(model.fc.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()

def run_epoch(train=True):
    dl = train_dl if train else valid_dl
    model.train() if train else model.eval()
    total=0; correct=0; loss_sum=0.0
    with torch.set_grad_enabled(train):
        for xb, yb in dl:
            xb, yb = xb.to(device), yb.to(device)
            if train: opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            if train: loss.backward(); opt.step()
            loss_sum += loss.item()*xb.size(0)
            correct += (logits.argmax(1)==yb).sum().item(); total += xb.size(0)
    return loss_sum/total, correct/total

hist_head = {'tr':[], 'va':[]}
for _ in range(5):
    tr_loss, tr_acc = run_epoch(train=True)
    va_loss, va_acc = run_epoch(train=False)
    hist_head['tr'].append((tr_loss, tr_acc)); hist_head['va'].append((va_loss, va_acc))

# 5) Unfreeze last block and use smaller LR
for p in model.layer4.parameters(): p.requires_grad = True
opt = torch.optim.Adam([
    {'params': model.fc.parameters(), 'lr': 1e-3},
    {'params': model.layer4.parameters(), 'lr': 3e-4},
])

hist_tune = {'tr':[], 'va':[]}
for _ in range(5):
    tr_loss, tr_acc = run_epoch(train=True)
    va_loss, va_acc = run_epoch(train=False)
    hist_tune['tr'].append((tr_loss, tr_acc)); hist_tune['va'].append((va_loss, va_acc))
```
Line‑by‑line
- Freeze: prevents backbone weights from updating; only the new head learns
- Replace head: output dims = n_classes
- Two phases: first stabilize head, then unfreeze last block with smaller LR to avoid catastrophic forgetting

---

Exercise 2 — Augmentation
```python
aug_tfms = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8,1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(), transforms.Normalize(mean, std)
])
train_ds_aug = datasets.ImageFolder(train_dir, transform=aug_tfms)
train_dl_aug = DataLoader(train_ds_aug, batch_size=64, shuffle=True, num_workers=0)

# Re-train head phase with augmentation for a few epochs
train_dl = train_dl_aug  # swap in
hist_aug = {'tr':[], 'va':[]}
for _ in range(5):
    tr_loss, tr_acc = run_epoch(train=True)
    va_loss, va_acc = run_epoch(train=False)
    hist_aug['tr'].append((tr_loss, tr_acc)); hist_aug['va'].append((va_loss, va_acc))
```
Notes
- RandomResizedCrop increases robustness to scale/position
- ColorJitter helps color invariance; use conservative ranges
- Expect slightly higher training loss but better generalization (val acc)

---

Exercise 3 — OneCycleLR
```python
# Reset optimizer for OneCycle
max_lr = 1e-3
steps_per_epoch = len(train_dl)
opt = torch.optim.Adam(model.parameters(), lr=max_lr)
sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=max_lr,
    epochs=5, steps_per_epoch=steps_per_epoch, pct_start=0.3, div_factor=10)

lrs = []
for epoch in range(5):
    model.train()
    for xb, yb in train_dl:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(); loss = loss_fn(model(xb), yb)
        loss.backward(); opt.step(); sched.step()
        lrs.append(sched.get_last_lr()[0])

plt.plot(lrs); plt.title('OneCycle LR'); plt.xlabel('Step'); plt.ylabel('LR'); plt.show()
```
Explanation
- OneCycle warms up to max_lr then cools down; often yields faster, smoother training
- Track LR over steps to verify schedule shape

Takeaways
- Start with head-only training to align classifier to features
- Unfreeze progressively with lower LR on deeper layers

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Load a small image folder with `ImageFolder` and `DataLoader`.

**How to reason about it:** ImageFolder derives class IDs from sorted directory names; preserve `class_to_idx`, use the selected weights' documented transforms, and start with `num_workers=0` for a portable first run.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Train only the classifier head for a few epochs.

**How to reason about it:** When training only the classifier head, pass only trainable head parameters to the optimizer and monitor validation loss and accuracy. Frozen parameters should have no gradients.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Unfreeze the final ResNet block and fine-tune it with a lower learning rate.

**How to reason about it:** Unfreezing the final block increases trainable capacity. Use a smaller backbone learning rate, keep the head rate explicit, and compare against the frozen baseline on the same split.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 4 — Transform mismatch diagnosis

**Prompt:** Compare predictions when validation images use the training transform with random crop/flip versus a deterministic validation transform. Explain the metric instability.

**Reasoning before implementation:** Augmentation belongs to training. Validation should apply deterministic resize/crop and the normalization expected by the selected weights.

Random validation transforms make the evaluation population change on every
pass, so metric movement can reflect crop luck rather than model changes.
Create separate dataset objects for train and validation transforms even when
they read the same directory structure.

Record transform configuration with the artifact; serving must reproduce the
deterministic inference transform exactly.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Frozen-state edge case

**Prompt:** Freeze a pretrained backbone containing BatchNorm. Explain the difference between `requires_grad=False` and putting frozen modules in evaluation mode.

**Reasoning before implementation:** requires_grad controls parameter gradients; train/eval controls BatchNorm running statistics and Dropout behavior.

A frozen parameter can still belong to a BatchNorm module whose running mean
and variance update in training mode. Decide whether to keep the frozen
backbone in eval mode while the head trains, and test that its buffers remain
unchanged.

When partially unfreezing, set modes deliberately rather than calling one
global `model.train()` and assuming freeze semantics are complete.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Offline fallback design

**Prompt:** Make the lesson runnable when pretrained weights are not cached. Detect cache availability, offer an explicit connected preload step, and provide a tiny randomly initialized CNN smoke path.

**Reasoning before implementation:** Never trigger an undocumented download. Report whether results use pretrained or random weights because their learning goals differ.

The default offline smoke path should validate dataset loading, shapes, forward
pass, loss, and one optimization step on generated images. It does not claim
transfer-learning quality. The optional connected path downloads the named
weight version once and documents the cache location.

On later offline runs, request that exact weight enum rather than an ambiguous
“latest” default. If absent, fail with a helpful message or select the clearly
labeled smoke fallback—never silently change the experiment.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
