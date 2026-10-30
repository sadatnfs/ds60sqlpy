# llm-020: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Initialization determines the scale of signals entering a network before learning. Large weights can create large activations, saturated probabilities or unstable gradients. Residual connections add another contribution to an existing representation, so scale and shape both matter. A single global norm can hide the first layer where a problem begins. Inspect intermediate activation norms and the gradients of named parameters on the same fixture. The comparison here changes only a fixed linear scale, making the resulting norm change calculable. A repair is meaningful when it restores finite behavior on the exact input that failed, not merely on a new easier input.

**Activation norm:** Magnitude of an intermediate representation.

**Initialization scale:** Magnitude policy for initial parameter values.

**Residual scale:** Relative contribution of an added transformation branch.

## Reading the implementation

Use torch.linalg.vector_norm to measure a tensor magnitude and torch.isfinite for elementwise checks. A matrix multiplied by a scalar scales linear outputs by that scalar. Autograd derivatives of a squared objective grow accordingly. Float32 multiplication by enormous values can overflow even when the input itself is finite. Keep the first nonfinite location in the diagnostic record.

## Exercise 1: Measure a small linear layer

The question is: Apply.01*identity to input[1,-1,2,-2].

The identity orientation preserves the input direction. Only scale changes, so the norm relation is independent of random projections.

```python
x = torch.tensor([[1.0, -1.0, 2.0, -2.0]])
small = 0.01 * torch.eye(4)
out = x @ small
np.testing.assert_allclose(
    torch.linalg.vector_norm(out).item(), 0.01 * np.sqrt(10), atol=1e-6, rtol=0
)
```

**Expected:** output norm.01*sqrt10.

**Verify:** Compare the computed values or written argument with output norm.01*sqrt10.

## Exercise 2: Increase only the scale

The question is: Replace.01*identity with 100*identity.

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

**Expected:** activation norm increases by factor10000.

**Verify:** Compare the computed values or written argument with activation norm increases by factor10000.

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

**Verify:** Compare the computed values or written argument with both finite; large-scale gradient norm is larger.

## Exercise 4: Find the first overflow

The question is: Apply a float32 matrix scaled1e38, then inspect matrix product and squared loss.

The diagnostic should identify the squared objective as nonfinite, while separately recording whether its input product already overflowed. One unlabelled NaN at the end is insufficient.

```python
extreme = x @ (torch.eye(4) * 1e38)
objective = extreme.square().mean()
assert not torch.isfinite(objective)
```

**Expected:** squared loss is nonfinite.

**Verify:** Compare the computed values or written argument with squared loss is nonfinite.

## Exercise 5: Repair on the same input

The question is: Restore the small scale and recalculate output and loss for the unchangedx.

Changing the fixture would not test the proposed repair. Reusing the original input isolates the effect of the initialization scale.

```python
repaired = x @ small
assert torch.isfinite(repaired).all() and torch.isfinite(repaired.square().mean())
```

**Expected:** both output and loss finite.

**Verify:** Compare the computed values or written argument with both output and loss finite.

## Exercise 6: Check residual dimensions

The question is: Compare residualx+x@small with an incompatible three-feature branch.

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

**Expected:** valid residual shape(1,4); width3 branch rejected.

**Verify:** Compare the computed values or written argument with valid residual shape(1,4); width3 branch rejected.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
