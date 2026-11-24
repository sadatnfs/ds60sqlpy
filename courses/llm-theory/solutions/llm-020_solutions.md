# llm-020: explanatory solutions

Read these initialization and residual scale answers after attempting *Measure a small linear layer* through *Check residual dimensions*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Trace gradients* points to one step. `llm-020_solution.py` holds the assertions; this page explains how they test activation norm. Then try *Check residual dimensions* on a fresh input you chose before looking.

## Mechanism review

Initialization determines the scale of signals entering a network before learning. Large weights can create large activations, saturated probabilities or unstable gradients. Residual connections add another contribution to an existing representation, so scale and shape both matter. A single global norm can hide the first layer where a problem begins. Inspect intermediate activation norms and the gradients of named parameters on the same fixture. The comparison here changes only a fixed linear scale, making the resulting norm change calculable. A repair is meaningful when it restores finite behavior on the exact input that failed, not merely on a new easier input.

**Activation norm:** Magnitude of an intermediate representation.

**Initialization scale:** Magnitude policy for initial parameter values.

**Residual scale:** Relative contribution of an added transformation branch.

## Reading the implementation

Use torch.linalg.vector_norm to measure a tensor magnitude and torch.isfinite for elementwise checks. A matrix multiplied by a scalar scales linear outputs by that scalar. Autograd derivatives of a squared objective grow accordingly. Float32 multiplication by enormous values can overflow even when the input itself is finite. Keep the first nonfinite location in the diagnostic record.

## Exercise 1: Measure a small linear layer

The question is: Apply 0.01*identity to input [1, -1, 2, -2].

The identity orientation preserves the input direction. Only scale changes, so the norm relation is independent of random projections.

```python
x = torch.tensor([[1.0, -1.0, 2.0, -2.0]])
small = 0.01 * torch.eye(4)
out = x @ small
np.testing.assert_allclose(
    torch.linalg.vector_norm(out).item(), 0.01 * np.sqrt(10), atol=1e-6, rtol=0
)
```

**Expected:** output norm \(0.01\sqrt{10}\).

**Verify:** For *Measure a small linear layer*, a fresh-process check confirms `torch.linalg.vector_norm(out).item()` matches `0.01 * np.sqrt(10)` within 1e-6.

## Exercise 2: Increase only the scale

The question is: Replace 0.01*identity with 100*identity.

Changing both scale and random orientation would confound the comparison. Here the factor follows directly from linearity.

```python
large = 100 * torch.eye(4)
bigger = x @ large
np.testing.assert_allclose(
    (torch.linalg.vector_norm(bigger) / torch.linalg.vector_norm(out)).item(),
    10000,
    atol=0.01,
    rtol=0,
)
```

**Expected:** activation norm increases by factor 10000.

**Verify:** For *Increase only the scale*, a fresh-process check confirms `(torch.linalg.vector_norm(bigger) / torch.linalg.vector_norm(out)).item()` matches `10000` within 0.01.

## Exercise 3: Trace gradients

The question is: Differentiate mean squared output for the small and large matrices and compare norms.

A finite forward output does not guarantee a useful gradient scale. Logging both makes a potential optimization problem visible before updates are applied.

```python
norms = []
for initial in [small, large]:
    w = initial.clone().requires_grad_()
    loss = (x @ w).square().mean()
    loss.backward()
    norms.append(w.grad.norm().item())
assert np.isfinite(norms).all() and norms[1] > norms[0]
```

**Expected:** both finite; large-scale gradient norm is larger.

**Verify:** For *Trace gradients*, a fresh-process check confirms `np.isfinite(norms).all()` and `norms[1] > norms[0]`.

## Exercise 4: Find the first overflow

The question is: Apply a float32 matrix scaled 1e38, then inspect matrix product and squared loss.

The diagnostic should identify the squared objective as nonfinite, while separately recording whether its input product already overflowed. One unlabelled NaN at the end is insufficient.

```python
extreme = x @ (torch.eye(4) * 1e38)
objective = extreme.square().mean()
assert not torch.isfinite(objective)
```

**Expected:** squared loss is nonfinite.

**Verify:** For *Find the first overflow*, a fresh-process check confirms `not torch.isfinite(objective)`.

## Exercise 5: Repair on the same input

The question is: Restore the small scale and recalculate output and loss for the unchanged x.

Changing the fixture would not test the proposed repair. Reusing the original input isolates the effect of the initialization scale.

```python
repaired = x @ small
assert torch.isfinite(repaired).all() and torch.isfinite(repaired.square().mean())
```

**Expected:** both output and loss finite.

**Verify:** For *Repair on the same input*, a fresh-process check confirms `torch.isfinite(repaired).all()` and `torch.isfinite(repaired.square().mean())`.

## Exercise 6: Check residual dimensions

The question is: Compare residual x+x@small with an incompatible three-feature branch.

Numeric scale and dimension compatibility are independent contracts. A stable norm cannot compensate for adding quantities with incompatible feature meaning.

```python
assert tuple((x + x @ small).shape) == (1, 4)
try:
    x + torch.ones((1, 3))
except RuntimeError:
    pass
else:
    raise AssertionError("incompatible residual accepted")
```

**Expected:** valid residual shape (1, 4); width 3 branch rejected.

**Verify:** For *Check residual dimensions*, a fresh-process check confirms `tuple((x + x @ small).shape) == (1, 4)` and `x + torch.ones((1, 3))` raises `RuntimeError`.

## Review after comparison

Change one input to *Find the first overflow* and predict the result first; keep *Check residual dimensions* failing beside the repair. Log a missing PyTorch separately from a wrong activation norm value in `llm-020`.
