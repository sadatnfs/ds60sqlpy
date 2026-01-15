# Day 47 — PyTorch Basics: Tensors, Modules, and the Training Loop (Companion Guide)

## Learning objectives
- Create tensors, move between CPU/GPU, and manage dtype/device
- Build models with nn.Module; write clear training/eval loops
- Use Datasets/DataLoaders, optimizers, schedulers, and checkpoints

## Why this matters
Mastering the training loop unlocks every deep learning project: you’ll debug faster, train reproducibly, and scale when needed.

## Core concepts and examples
### Tensors and device
```python
import torch
x = torch.randn(32, 100)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
x = x.to(device)
```

### Dataset and DataLoader
```python
from torch.utils.data import Dataset, DataLoader
class MyDS(Dataset):
    def __init__(self, X, y): self.X, self.y = X, y
    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]

dls = DataLoader(MyDS(X_train, y_train), batch_size=64, shuffle=True, num_workers=2)
```

### Model, loss, optimizer
```python
import torch.nn as nn
class MLP(nn.Module):
    def __init__(self, inp, hid, out):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(inp, hid), nn.ReLU(),
            nn.Linear(hid, out)
        )
    def forward(self, x): return self.net(x)

model = MLP(X_train.shape[1], 128, n_classes).to(device)
loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
```

### Training/eval loop
```python
def train_epoch(model, dloader):
    model.train(); total=0; correct=0; loss_sum=0.0
    for xb, yb in dloader:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad()
        logits = model(xb)
        loss = loss_fn(logits, yb)
        loss.backward(); opt.step()
        loss_sum += loss.item()*xb.size(0)
        correct += (logits.argmax(1)==yb).sum().item(); total += xb.size(0)
    return loss_sum/total, correct/total

@torch.no_grad()
def evaluate(model, dloader):
    model.eval(); total=0; correct=0; loss_sum=0.0
    for xb, yb in dloader:
        xb, yb = xb.to(device), yb.to(device)
        logits = model(xb)
        loss = loss_fn(logits, yb)
        loss_sum += loss.item()*xb.size(0)
        correct += (logits.argmax(1)==yb).sum().item(); total += xb.size(0)
    return loss_sum/total, correct/total
```

### Checkpointing
```python
torch.save({'model': model.state_dict(), 'opt': opt.state_dict()}, 'chkpt.pt')
# load: ckpt = torch.load('chkpt.pt', map_location=device); model.load_state_dict(ckpt['model'])
```

## Common pitfalls
- Forgetting `.train()`/`.eval()`; batchnorm/dropout behave differently
- Not zeroing gradients before backward; grads accumulate
- Mismatched shapes/dtypes for loss functions (e.g., Long for class labels)

## Practice exercises
1) Implement early stopping on validation loss
2) Add a StepLR scheduler and compare convergence
3) Add mixed precision training with torch.cuda.amp

## Further reading
- PyTorch docs: https://pytorch.org/docs/stable/index.html
- Training loops: https://pytorch.org/tutorials/beginner/introyt/trainingyt.html
