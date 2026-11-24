# llm-015: explanatory solutions

Read these pyTorch tensors and automatic gradients answers after attempting *Derive a scalar gradient* through *Check an embedding table*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Observe accumulation* points to one step. `llm-015_solution.py` holds the assertions; this page explains how they test autograd. Then try *Check an embedding table* on a fresh input you chose before looking.

## Mechanism review

PyTorch builds a dynamic computation graph when operations involve tensors requiring gradients. backward traverses that graph and accumulates derivatives into leaf gradients. A detached tensor keeps numeric data while removing its gradient connection, which can silently break training if used in the forward path. A zero derivative and an absent gradient are different observations. Embedding lookup is still the same indexed table seen in the NumPy lesson; a framework adds trainable state and gradient tracking rather than changing the mathematical meaning. CPU execution and tiny fixtures keep the first framework investigation inspectable.

**Autograd:** Automatic differentiation through recorded tensor operations.

**Leaf gradient:** Accumulated derivative stored on an input or parameter tensor.

**Detach:** Remove a tensor value from its existing gradient graph.

## Reading the implementation

torch.tensor(..., requires_grad=True) creates a leaf whose .grad is populated after backward. Clear gradients before a new independent step because backward accumulates by default. detach returns a value with requires_grad=False. nn.Embedding.from_pretrained(..., freeze=False) wraps a fixed literal table as trainable state. IDs use torch.long and select rows along the vocabulary axis.

## Exercise 1: Derive a scalar gradient

The question is: Differentiate(w-2)² at w=0 in float64.

The analytic derivative \(2(w-2)\) supplies an independent oracle. A correct loss alone would not show that the gradient graph was connected.

```python
w = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
loss = (w - 2) ** 2
loss.backward()
assert w.grad.item() == -4 and loss.item() == 4
```

**Expected:** gradient -4 and loss 4.

**Verify:** For *Derive a scalar gradient*, a fresh-process check confirms `w.grad.item() == -4` and `loss.item() == 4`.

## Exercise 2: Compare finite differences

The question is: Use central difference h=0.001 for the same scalar function.

Finite differences perturb the function value rather than reading autograd internals. Agreement away from a nondifferentiable point supports the derivative calculation.

```python
h = 0.001
numeric = (((h - 2) ** 2) - ((-h - 2) ** 2)) / (2 * h)
np.testing.assert_allclose(numeric, -4, atol=1e-10, rtol=0)
```

**Expected:** finite difference approximately -4 within 1e-10.

**Verify:** For *Compare finite differences*, a fresh-process check confirms `numeric` matches `-4` within 1e-10.

## Exercise 3: Observe accumulation

The question is: Call backward on a new loss without clearing the prior gradient.

PyTorch adds to existing gradients. A training loop that forgets zero_grad changes its effective update and can look unstable for reasons unrelated to model capacity.

```python
((w - 2) ** 2).backward()
assert w.grad.item() == -8
```

**Expected:** stored gradient becomes -8.

**Verify:** For *Observe accumulation*, a fresh-process check confirms `w.grad.item() == -8`.

## Exercise 4: Clear gradient state

The question is: Set the gradient to None, recompute and backpropagate once.

Resetting before the next independent batch restores the intended one-batch derivative. Intentional accumulation needs a separate denominator and step policy.

```python
w.grad = None
((w - 2) ** 2).backward()
assert w.grad.item() == -4
```

**Expected:** gradient returns to -4.

**Verify:** For *Clear gradient state*, a fresh-process check confirms `w.grad.item() == -4`.

## Exercise 5: Inspect detachment

The question is: Detach w and compare its value and gradient-tracking status.

Detach preserves a numeric observation while cutting dependency. It is appropriate for logging or explicit stop-gradient designs, but not a repair for an unexplained backward error.

```python
detached = w.detach()
assert detached.item() == 0 and detached.requires_grad is False
```

**Expected:** same value 0; requires_gradFalse.

**Verify:** For *Inspect detachment*, a fresh-process check confirms `detached.item() == 0` and `detached.requires_grad is False`.

## Exercise 6: Check an embedding table

The question is: Lookup IDs 2, 0, 2 in a fixed 4x2 table and compare repeated rows.

The lookup does not average repeated IDs. Both positions refer to the same parameter row, so later gradient contributions to that row can accumulate.

```python
table = torch.tensor([[1.0, 0.0], [0.0, 1.0], [2.0, 2.0], [-1.0, 1.0]])
embedding = nn.Embedding.from_pretrained(table, freeze=False)
out = embedding(torch.tensor([2, 0, 2]))
assert tuple(out.shape) == (3, 2)
np.testing.assert_array_equal(out.detach().numpy(), [[2, 2], [1, 0], [2, 2]])
```

**Expected:** shape (3, 2); rows 0 and 2 both [2, 2].

**Verify:** For *Check an embedding table*, a fresh-process check confirms `tuple(out.shape) == (3, 2)` and `out.detach().numpy()` equals `[[2, 2], [1, 0], [2, 2]]`.

## Review after comparison

Change one input to *Clear gradient state* and predict the result first; keep *Inspect detachment* failing beside the repair. Log a missing PyTorch separately from a wrong autograd value in `llm-015`.
