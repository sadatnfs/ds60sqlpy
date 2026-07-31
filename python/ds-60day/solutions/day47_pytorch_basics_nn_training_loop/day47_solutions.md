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

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`DataLoader(dataset, batch_size=..., shuffle=...)`:** yields bounded feature/target batches and controls training order.
2. **`model(features)`:** returns logits shaped `(batch, classes)` for multiclass classification.
3. **`CrossEntropyLoss(logits, labels)`:** expects floating logits and `long` class indices shaped `(batch,)`.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** The solution establishes tensor contracts first, then separates training updates from evaluation measurement and checkpoint policy.

**Useful alternative:** Full-batch training is simpler for tiny data; high-level trainers reduce boilerplate but can hide the exact state transitions learners need to understand.

**Trade-off:** Smaller batches add gradient noise and more updates; larger batches use more memory and may generalize differently.

**Edge case to test:** Empty loaders, a final partial batch, wrong class count, device mismatch, non-finite loss, and checkpointing optimizer state require tests.

**Evidence of correctness:** Overfit a tiny batch, assert logits/label contracts, show dropout mode behavior, use no-grad validation, aggregate loss by example, and reload a portable checkpoint.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Reasoning notes for original Exercise 1

**Prompt:** Add dropout to the MLP and compare results.

**How to reason about it:** Dropout is active only in training mode and its effect is noisy. Compare seeded runs or validation curves, and place it deliberately after an activation rather than assuming one final score proves benefit.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Add dropout to the MLP and compare results`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Reasoning notes for original Exercise 2

**Prompt:** Implement a small minibatch training loop with `DataLoader`.

**How to reason about it:** A minibatch loop keeps zero-grad, forward, loss, backward, and step inside the batch iteration. Shuffle training only, use float features and class-index long targets, and aggregate epoch metrics by support.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Implement a small minibatch training loop with DataLoader`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Exercise 3 — Shape and dtype contract

**Prompt:** Write assertions at the start of a classification training step for feature shape/dtype, target shape/dtype, and logits shape.

**Reasoning before implementation:** CrossEntropyLoss expects floating logits `(batch, classes)` and integer class indices `(batch,)` with dtype long.

```python
def validate_classification_batch(features, targets, logits, class_count):
    assert features.ndim == 2 and features.is_floating_point()
    assert targets.ndim == 1 and targets.dtype == torch.long
    assert logits.shape == (features.shape[0], class_count)
    assert torch.isfinite(logits).all()
```

One-hot targets require a different explicit contract. Avoid `squeeze()`
without a dimension because a batch of size one can lose its batch axis.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Write assertions at the start of a classification training step for feature shape/dtype, targ...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 4 — Validation implementation

**Prompt:** Implement an evaluation function that returns sample-weighted loss and accuracy, restores the caller's prior train/eval mode, and never retains an autograd graph.

**Reasoning before implementation:** Remember `was_training = model.training`, call eval and no_grad, aggregate counts, then restore train mode only if it was previously active.

Save mode before validation so a reusable helper does not unexpectedly alter
its caller. Sum loss times batch size and correct predictions, divide by the
total, and raise for an empty loader.

`torch.inference_mode()` is an even stronger evaluation context when its
restrictions fit. Keep all returned values as plain Python numbers so the
history does not retain tensors or device memory.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Implement an evaluation function that returns sample-weighted loss and accuracy, restores the...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 5 — DataLoader reproducibility

**Prompt:** Run two shuffled DataLoaders with the same seed and compare batch order. Then state what changes when using worker processes.

**Reasoning before implementation:** Pass a seeded `torch.Generator`; worker initialization and external NumPy/Python randomness need their own deliberate seeds.

Use a generator created specifically for the training loader so other random
draws do not silently advance its state. With multiple workers, seed each
worker's Python/NumPy operations and keep transforms deterministic for the
comparison.

Exact reproducibility can vary across devices and algorithms. Record device,
PyTorch version, deterministic settings, and seed; also test that conclusions
hold across more than one seed.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Run two shuffled DataLoaders with the same seed and compare batch order. Then state what chan...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Exercise 6 — Portable checkpoint

**Prompt:** Save model, optimizer, epoch, metric history, and configuration, then reload on CPU and resume one step. Explain `state_dict` versus serializing the entire model object.

**Reasoning before implementation:** Save plain state dictionaries plus architecture/config metadata. Use `map_location='cpu'` and recreate the model class before loading.

State dictionaries are less coupled to source-module paths than pickling a
whole model object. Validate configuration and tensor shapes before loading,
then set the intended mode explicitly.

Checkpoint files are still loaded through PyTorch serialization and should be
treated as trusted artifacts. Save RNG state as well when exact mid-run resume
is a requirement.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Save model, optimizer, epoch, metric history, and configuration, then reload on CPU and resum...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.
