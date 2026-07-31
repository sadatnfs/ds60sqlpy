# Day 46 — Solutions: Deep Learning Overview

In these solutions we implement a tiny MLP, compare optimizers, and deeply explain vanishing/exploding gradients and mitigations. Each code block is followed by a line‑by‑line walkthrough.

Contents
- Exercise 1: Tiny MLP on toy data; vary depth/width to observe overfitting
- Exercise 2: Compare SGD vs Adam on convergence speed
- Exercise 3: Explain vanishing/exploding gradients and mitigation strategies

---

Setup
```python
# 1) Imports
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt
import numpy as np

# 2) Reproducibility and device
torch.manual_seed(0)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 3) Toy regression dataset: y = sin(x) + noise
n = 200
x = torch.linspace(-3, 3, n).unsqueeze(1)
y = torch.sin(x) + 0.15*torch.randn_like(x)

# 4) Train/valid split
idx = torch.randperm(n)
train_idx, valid_idx = idx[:160], idx[160:]
Xtr, ytr = x[train_idx], y[train_idx]
Xva, yva = x[valid_idx], y[valid_idx]

# 5) Dataloaders
bs = 32
tr_dl = DataLoader(TensorDataset(Xtr, ytr), batch_size=bs, shuffle=True)
va_dl = DataLoader(TensorDataset(Xva, yva), batch_size=bs)
```
Explanation
- Imports: torch core, nn modules, DataLoader utilities, plotting
- Seed: fixes random draws for comparable runs; device: CUDA if available
- Data: 200 evenly spaced x in [-3,3]; target is sin with Gaussian noise
- Split: 160 train / 40 valid via random permutation indices
- Dataloaders: mini-batches for stochastic gradient descent

---

Worked reference for Exercise 1 — Tiny MLP and capacity exploration
```python
class MLP(nn.Module):
    def __init__(self, width=32, depth=2):
        super().__init__()
        layers = []
        inp = 1
        for _ in range(depth):
            layers += [nn.Linear(inp, width), nn.Tanh()]
            inp = width
        layers += [nn.Linear(inp, 1)]
        self.net = nn.Sequential(*layers)
    def forward(self, x):
        return self.net(x)

# Train helper
def fit(model, dl_tr, dl_va, epochs=500, lr=1e-2):
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    tr_hist, va_hist = [], []
    for ep in range(epochs):
        model.train(); tr_loss = 0.0; ntr = 0
        for xb, yb in dl_tr:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            preds = model(xb)
            loss = loss_fn(preds, yb)
            loss.backward(); opt.step()
            tr_loss += loss.item()*xb.size(0); ntr += xb.size(0)
        # valid
        model.eval(); va_loss = 0.0; nva = 0
        with torch.no_grad():
            for xb, yb in dl_va:
                xb, yb = xb.to(device), yb.to(device)
                loss = loss_fn(model(xb), yb)
                va_loss += loss.item()*xb.size(0); nva += xb.size(0)
        tr_hist.append(tr_loss/ntr); va_hist.append(va_loss/nva)
    return tr_hist, va_hist

# Compare small vs big capacity
small = MLP(width=16, depth=1)
big   = MLP(width=128, depth=4)
tr_s, va_s = fit(small, tr_dl, va_dl, epochs=800, lr=5e-3)
tr_b, va_b = fit(big,   tr_dl, va_dl, epochs=800, lr=5e-3)

# Plot learning curves
plt.plot(tr_s, label='small train'); plt.plot(va_s, label='small valid')
plt.plot(tr_b, label='big train');   plt.plot(va_b, label='big valid')
plt.yscale('log'); plt.legend(); plt.title('Learning curves'); plt.show()
```
Walkthrough
- MLP: stack [Linear, Tanh] blocks depth times, then a final Linear to 1
- fit: standard loop with Adam and MSE; track epoch-averaged train/valid loss
- small vs big: small capacity may underfit; big capacity likely drives train loss down faster and may overfit (train<<valid)
- Plot: use log y-scale to see separation; takeaway is bias/variance tradeoff

---

Worked reference for Exercise 2 — SGD vs Adam convergence
```python
def fit_with_opt(model, opt_ctor, lr=1e-2, epochs=400):
    model = model.to(device)
    opt = opt_ctor(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    tr_hist = []
    for _ in range(epochs):
        model.train(); loss_sum=0.0; n=0
        for xb, yb in tr_dl:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad(); loss = loss_fn(model(xb), yb)
            loss.backward(); opt.step()
            loss_sum += loss.item()*xb.size(0); n += xb.size(0)
        tr_hist.append(loss_sum/n)
    return tr_hist

model_sgd  = MLP(width=64, depth=3)
model_adam = MLP(width=64, depth=3)
sgd_hist  = fit_with_opt(model_sgd,  torch.optim.SGD,  lr=1e-2, epochs=600)
adam_hist = fit_with_opt(model_adam, torch.optim.Adam, lr=1e-3, epochs=600)

plt.plot(sgd_hist, label='SGD lr=1e-2')
plt.plot(adam_hist, label='Adam lr=1e-3')
plt.yscale('log'); plt.legend(); plt.title('Convergence speed'); plt.show()
```
Explanation
- fit_with_opt: swaps optimizer constructor; all else same
- Hyperparameters: SGD often needs larger lr; Adam converges faster initially
- Expectation: Adam’s curve typically descends more smoothly early on

---

Worked reference for Exercise 3 — Vanishing/exploding gradients and mitigation

Concepts
- Vanishing: gradients shrink through depth (e.g., sigmoids/tanh saturate); early layers update slowly
- Exploding: gradients blow up through multiplications; unstable updates

Mitigations
- Nonlinearities: prefer ReLU/variants; avoid deep sigmoids without care
- Initialization: He (ReLU) or Xavier (tanh) to keep variance stable
- Normalization: BatchNorm/LayerNorm stabilize activations/gradients
- Residual connections: ease gradient flow in deep nets
- Gradient clipping: cap global norm to prevent blow-ups

Code sketch with good defaults
```python
class StableMLP(nn.Module):
    def __init__(self, width=128, depth=6):
        super().__init__()
        layers = []
        layers += [nn.Linear(1, width), nn.ReLU(), nn.BatchNorm1d(width)]
        for _ in range(depth-1):
            layers += [nn.Linear(width, width), nn.ReLU(), nn.BatchNorm1d(width)]
        layers += [nn.Linear(width, 1)]
        self.net = nn.Sequential(*layers)
        # Kaiming initialization for ReLU
        for m in self.net:
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight)
                nn.init.zeros_(m.bias)
    def forward(self, x): return self.net(x)

m = StableMLP().to(device)
opt = torch.optim.Adam(m.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()
for xb, yb in tr_dl:
    xb, yb = xb.to(device), yb.to(device)
    opt.zero_grad(); loss = loss_fn(m(xb), yb)
    loss.backward()
    nn.utils.clip_grad_norm_(m.parameters(), max_norm=1.0)  # gradient clipping
    opt.step()
```
Line‑by‑line highlights
- BatchNorm after ReLU reduces internal covariate shift; stabilizes gradients
- He/Kaiming init matches ReLU to keep layer output variance near constant
- clip_grad_norm_ prevents a single step from exploding parameter updates

Takeaway
- Combine proper nonlinearity, init, normalization, residuals, and clipping for stable deep training.

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`tensor.requires_grad_(True)`:** marks a leaf tensor whose derivative should be accumulated.
2. **`loss.backward()`:** computes derivatives through the recorded graph and adds them to existing `.grad` values.
3. **`optimizer.zero_grad(); ...; optimizer.step()`:** clears old gradients, computes a new step, and updates registered parameters.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** A scalar derivative proves autograd mechanics before the full loop connects gradients to controlled parameter updates.

**Useful alternative:** Automatic differentiation is safer than hand derivatives for complex graphs; closed-form or scikit-learn models may be simpler for small structured problems.

**Trade-off:** More network capacity can fit complex patterns but raises optimization, data, compute, and overfitting risk.

**Edge case to test:** Wrong dtype/device, unintended broadcasting, detached tensors, retained graphs, or non-finite loss can make training fail or silently optimize the wrong quantity.

**Evidence of correctness:** Check a hand-computable gradient, assert shapes/dtypes, show parameters change after one step, separate train/eval modes, and report both training and validation behavior.

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

### Exercise 1 — Original lesson practice

**Prompt:** Plot the loss over epochs.

**How to reason about it:** Store one scalar loss per epoch after aggregating by example, not an arbitrary last batch. Compare train and validation curves and label the optimizer, learning rate, seed, and capacity.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — tensors, computation graphs, gradients, and the optimizer cycle — save a labeled epoch-versus-loss curve and print the raw loss sequence; assert every plotted point is the sample-weighted epoch loss and report whether the final value improved over epoch 1.

### Exercise 2 — Original lesson practice

**Prompt:** Replace SGD with Adam and compare convergence.

**How to reason about it:** Recreate identically initialized models for optimizer comparisons. Adam and SGD often need different learning rates, so compare documented tuning budgets rather than forcing one shared setting.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — tensors, computation graphs, gradients, and the optimizer cycle — from identical initial weights, batches, epochs, and seed, print SGD and Adam loss per epoch plus final validation loss; report convergence behavior without declaring a winner from unequal settings.

### Exercise 3 — Original lesson practice

**Prompt:** Add one hidden layer and a ReLU activation.

**How to reason about it:** A hidden layer adds capacity only when dimensions and activation order are correct. Track `(batch, features)` through Linear-ReLU-Linear and compare validation evidence, not merely lower training loss.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — tensors, computation graphs, gradients, and the optimizer cycle — assert the network's layer dimensions and output shape on a fixed batch, then compare parameter count and validation loss with the original model under the same seed/optimizer budget.

### Exercise 4 — Autograd tracing

**Prompt:** For one scalar regression batch, annotate every line from `zero_grad()` through `step()`: which tensors receive gradients, when are they accumulated, and when do parameters change?

**Reasoning before implementation:** Gradients accumulate in parameter `.grad` fields during backward; the optimizer reads them during step. zero_grad clears the previous batch.

Forward computation builds an autograd graph because model parameters require
gradients. `loss.backward()` applies the chain rule and *adds* into each
parameter's `.grad`. `optimizer.step()` then updates parameter values; it does
not clear gradients.

Call `zero_grad()` once per optimization step before backward. Deliberate
gradient accumulation is possible, but then scale the loss and document the
effective batch size. Inspect at least one gradient norm and assert it is
finite before the update.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Autograd tracing — print parameter value, gradient before/after zero_grad, gradient after backward, and parameter after step for one fixed batch; assert accumulation occurs across backward calls until zeroed and only step changes parameters.

### Exercise 5 — Mode debugging

**Prompt:** Build a model with Dropout and BatchNorm, then compare repeated predictions in `train()` and `eval()` modes. Explain why `torch.no_grad()` is related but not interchangeable.

**Reasoning before implementation:** Mode changes module behavior; no_grad disables graph recording. Validation usually needs both `model.eval()` and `with torch.no_grad()`.

Dropout remains random in training mode, and BatchNorm updates/runs from batch
statistics. Evaluation mode disables Dropout and uses stored BatchNorm state.
`no_grad()` saves memory and prevents gradient tracking, but it does not switch
those modules into evaluation behavior.

After validation, call `model.train()` before the next training epoch. A common
bug is evaluating correctly once and then continuing training while the model
is still in evaluation mode.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Mode debugging — for one fixed input, print repeated train-mode and eval-mode outputs plus BatchNorm running statistics; assert eval outputs are repeatable, no_grad removes graph tracking, and the caller restores the intended mode.

### Exercise 6 — Loss-aggregation edge case

**Prompt:** Compare averaging per-batch losses with a sample-weighted epoch loss when the final batch is smaller. Implement the correct aggregation.

**Reasoning before implementation:** Multiply each mean batch loss by batch size, sum, then divide by the number of examples.

```python
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

features = torch.arange(10, dtype=torch.float32).reshape(-1, 1)
targets = 2 * features + 1
data_loader = DataLoader(
    TensorDataset(features, targets),
    batch_size=4,
    shuffle=False,
)
model = nn.Linear(1, 1)
loss_function = nn.MSELoss(reduction="mean")

loss_sum = 0.0
example_count = 0
for batch_features, batch_targets in data_loader:
    predictions = model(batch_features)
    loss = loss_function(predictions, batch_targets)
    loss_sum += float(loss.item()) * batch_features.size(0)
    example_count += batch_features.size(0)

epoch_loss = loss_sum / example_count
with torch.no_grad():
    direct_loss = float(loss_function(model(features), targets).item())
assert abs(epoch_loss - direct_loss) < 1e-4 * max(1.0, abs(direct_loss))
```

An unweighted mean of batch means gives the short final batch the same weight
as every full batch. It is correct only when all batches are the same size or
the loss function returns a sum and the denominator is handled accordingly.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Loss-aggregation edge case — with unequal final-batch size, print each batch loss/count, naive mean, weighted epoch loss, and direct full-dataset loss; assert weighted and direct losses agree within 1e-7 while the naive mean differs.
