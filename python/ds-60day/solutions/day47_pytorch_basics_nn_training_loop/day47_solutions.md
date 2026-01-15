# Day 47 — Solutions: PyTorch Basics, Modules, and the Training Loop

We build a minimal, correct training loop; add early stopping; add a LR scheduler; and enable mixed precision training. After each code block you’ll find a line‑by‑line explanation.

Contents
- Exercise 1: Implement early stopping on validation loss
- Exercise 2: Add StepLR and compare convergence
- Exercise 3: Add mixed precision with torch.cuda.amp

---

Setup
```python
# 1) Imports
import torch, torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

# 2) Device and reproducibility
torch.manual_seed(0)
np.random.seed(0)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 3) Data: simple classification problem
X, y = make_classification(n_samples=5000, n_features=20, n_informative=10,
                           class_sep=1.0, random_state=0)
Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
tr_ds = TensorDataset(torch.tensor(Xtr, dtype=torch.float32), torch.tensor(ytr, dtype=torch.long))
va_ds = TensorDataset(torch.tensor(Xva, dtype=torch.float32), torch.tensor(yva, dtype=torch.long))
tr_dl = DataLoader(tr_ds, batch_size=128, shuffle=True)
va_dl = DataLoader(va_ds, batch_size=256)

# 4) Model
class MLP(nn.Module):
    def __init__(self, inp, hid, out):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(inp, hid), nn.ReLU(),
            nn.Linear(hid, hid), nn.ReLU(),
            nn.Linear(hid, out)
        )
    def forward(self, x):
        return self.net(x)

model = MLP(20, 128, 2).to(device)
loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
```
Explanation
- make_classification: tabular signal that’s easy to learn but nontrivial
- Dataloaders: larger batch for eval since no backprop; faster
- MLP: two hidden layers with ReLU, final logits of shape [B, 2]
- CrossEntropyLoss expects logits and Long labels 0..C-1

---

Exercise 1 — Early stopping on validation loss
```python
class EarlyStopper:
    def __init__(self, patience=10, min_delta=0.0):
        self.patience, self.min_delta = patience, min_delta
        self.best = float('inf'); self.bad = 0
    def step(self, metric):
        if metric < self.best - self.min_delta:
            self.best = metric; self.bad = 0; return False  # keep training
        self.bad += 1
        return self.bad >= self.patience  # True => stop

def train_one_epoch(model, dl, opt, loss_fn):
    model.train(); total=0; correct=0; loss_sum=0.0
    for xb, yb in dl:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(); logits = model(xb)
        loss = loss_fn(logits, yb); loss.backward(); opt.step()
        loss_sum += loss.item()*xb.size(0)
        correct += (logits.argmax(1)==yb).sum().item(); total += xb.size(0)
    return loss_sum/total, correct/total

@torch.no_grad()
def evaluate(model, dl, loss_fn):
    model.eval(); total=0; correct=0; loss_sum=0.0
    for xb, yb in dl:
        xb, yb = xb.to(device), yb.to(device)
        logits = model(xb); loss = loss_fn(logits, yb)
        loss_sum += loss.item()*xb.size(0)
        correct += (logits.argmax(1)==yb).sum().item(); total += xb.size(0)
    return loss_sum/total, correct/total

# Training loop with early stopping
stopper = EarlyStopper(patience=8, min_delta=1e-4)
hist = {'tr_loss':[], 'va_loss':[], 'va_acc':[]}
for epoch in range(200):
    tr_loss, _ = train_one_epoch(model, tr_dl, opt, loss_fn)
    va_loss, va_acc = evaluate(model, va_dl, loss_fn)
    hist['tr_loss'].append(tr_loss); hist['va_loss'].append(va_loss); hist['va_acc'].append(va_acc)
    if stopper.step(va_loss):
        print(f"Early stopped at epoch {epoch}"); break

plt.plot(hist['tr_loss'], label='train'); plt.plot(hist['va_loss'], label='valid')
plt.yscale('log'); plt.legend(); plt.title('Loss'); plt.show()
print(f"Best val acc: {max(hist['va_acc']):.3f}")
```
Line‑by‑line
- EarlyStopper tracks best validation loss; stops after patience epochs without improvement ≥ min_delta
- train_one_epoch: zero grads → forward → loss.backward → opt.step; accumulate loss and accuracy
- evaluate: model.eval and no_grad disable dropout/bn updates and grads
- Loop: record metrics, check stopper; plot to verify no overfitting after stop

---

Exercise 2 — StepLR scheduler
```python
# Reset model and optimizer for a fair comparison
model2 = MLP(20, 128, 2).to(device)
opt2 = torch.optim.SGD(model2.parameters(), lr=0.1, momentum=0.9)
sched = torch.optim.lr_scheduler.StepLR(opt2, step_size=20, gamma=0.1)

tr2, va2 = [], []
for epoch in range(60):
    tr_loss, _ = train_one_epoch(model2, tr_dl, opt2, loss_fn)
    va_loss, _ = evaluate(model2, va_dl, loss_fn)
    tr2.append(tr_loss); va2.append(va_loss)
    sched.step()

plt.plot(va2, label='SGD+StepLR val loss'); plt.yscale('log'); plt.legend(); plt.show()
print('Final LR:', sched.get_last_lr()[0])
```
Explanation
- SGD benefits from higher initial LR, then LR decay to refine
- StepLR reduces LR by gamma every step_size epochs; observe loss drops after LR steps

---

Exercise 3 — Mixed precision training
```python
scaler = torch.cuda.amp.GradScaler(enabled=(device.type=='cuda'))
model3 = MLP(20, 128, 2).to(device)
opt3 = torch.optim.Adam(model3.parameters(), lr=1e-3)

tr3 = []
for epoch in range(20):
    model3.train(); loss_sum=0.0; n=0
    for xb, yb in tr_dl:
        xb, yb = xb.to(device), yb.to(device)
        opt3.zero_grad()
        with torch.cuda.amp.autocast(enabled=(device.type=='cuda')):
            logits = model3(xb)
            loss = loss_fn(logits, yb)
        scaler.scale(loss).backward()
        scaler.step(opt3)
        scaler.update()
        loss_sum += loss.item()*xb.size(0); n += xb.size(0)
    tr3.append(loss_sum/n)

plt.plot(tr3); plt.yscale('log'); plt.title('AMP training loss'); plt.show()
```
Line‑by‑line
- GradScaler and autocast enable float16 math on CUDA with safe dynamic loss scaling
- scaler.scale(loss).backward and scaler.step handle underflow/overflow automatically
- On CPU, enabled=False makes this a no‑op; code still runs
