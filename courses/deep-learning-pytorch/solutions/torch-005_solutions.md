# torch-005: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A derivative measures local sensitivity: how much a function changes for a small input change. It is not itself a new parameter value. Gradient descent combines the derivative with a learning rate and a subtraction rule. PyTorch tracks operations involving tensors with `requires_grad=True` and can calculate a derivative through `autograd.grad`. A central finite difference estimates the same slope by evaluating the function at nearby inputs, providing an independent numerical check.

Finite differences involve a tradeoff: large steps measure a wider region, while extremely small steps lose precision through subtractive cancellation. Float64 is useful for this small diagnostic. At a nondifferentiable kink, a framework's chosen subgradient convention need not equal a symmetric finite difference. This lesson uses a smooth quadratic so the expected derivative is exact and the comparison is interpretable.

**Derivative:** The local rate of change of a function.

**Finite difference:** A numerical slope estimate from nearby function evaluations.

**Learning rate:** A multiplier converting a gradient into an update magnitude.

## Reading the implementation

For \(f(w)=(w-2)^2\), the analytic derivative is \(2(w-2)\). Construct a scalar float64 tensor with `requires_grad=True`, calculate f, and request `autograd.grad(f, w)`. The returned tensor does not automatically populate `w.grad`. A central difference uses \(\frac{f(w+h)-f(w-h)}{2h}\). Validate positive finite h and finite function values before comparing.

## Derive the slope before using it as an update

For \(f(w)=(w-2)^2\), expand the derivative or apply the square rule to obtain \(f'(w)=2(w-2)\). At \(w=0\) the loss is four and the derivative is -4. These are different quantities with different units: the derivative measures loss change per unit of w. A learning rate converts that sensitivity into a chosen parameter displacement. With learning rate \(\eta=0.1\), the update is \(w_{\mathrm{new}}=0-0.1(-4)=0.4\) and the recomputed loss is \(f(0.4)=(0.4-2)^2=2.56\).

The central finite difference uses two probes separated by 2 h:

\(D_h=\frac{f(w+h)-f(w-h)}{2h}\).

Expanding this particular quadratic gives \(f(w+h)-f(w-h)=4h(w-2)\), so \(D_h=2(w-2)\) exactly in real arithmetic. This special cancellation explains why the three supplied h values agree unusually well. It does not establish that central differences are exact for arbitrary nonlinear functions. For a sufficiently smooth general function, the leading truncation error is proportional to h² and a third derivative near the probe point.

A forward difference has a different error even on this quadratic. At zero, \(\frac{f(h)-f(0)}{h}=-4+h\). Thus \(h=0.1\) gives -3.9, \(h=0.01\) gives -3.99, and \(h=0.001\) gives -3.999. The visible offset is a property of the numerical approximation, not an autograd error. Deriving the approximation's expected bias prevents a correct implementation from being rejected for the wrong reason.

Floating-point cancellation pushes in the opposite direction from truncation error. As h shrinks, the two function values can become nearly equal compared with their magnitude. Their subtraction can lose meaningful digits, and a sufficiently small perturbation may not change the represented point at all. Scaling, dtype and the function's local behavior all matter. Sweep several probe scales and inspect the error curve rather than applying a universal h or tolerance.

The probe distance h is not the optimizer learning rate. A probe estimates local sensitivity without choosing a training trajectory; an update deliberately changes model state. A negative derivative identifies a locally descending direction, but a large finite update can still overshoot. For the supplied quadratic, a rate 1.1 update from zero moves to 4.4 and increases loss to 5.76, despite using the correct derivative.

For \(f(w)=|w|\) around zero, the left slope is -1 and the right slope is +1. A symmetric probe returns zero because the sides cancel, even though no unique ordinary derivative exists. ReLU gives a related counterexample: its symmetric slope at zero is 0.5 while PyTorch's selected backward convention is zero. Use a smooth point when checking equality with a classical derivative; at a kink, explain the convention separately.

Finally, `autograd.grad` returns the requested derivatives. It does not mean that the leaf's `.grad` buffer was populated. The return tuple and the accumulation behavior of `backward` are separate interfaces. [PyTorch 2.9 autograd.grad](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad.html). A returned -4 with `w.grad` still `None` is therefore expected here, while a genuinely disconnected path requires a different diagnosis.

## Exercise 1: Derive a scalar slope

The question is: Differentiate \({\left(w-2\right)}^{2}\) at \(w=0\) using `autograd.grad`.

The analytic derivative provides an oracle independent of autograd. The negative sign means increasing w locally decreases the loss.

```python
w = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
loss = (w - 2) ** 2
gradient = torch.autograd.grad(loss, w)[0]
assert gradient.item() == -4 and loss.item() == 4
```

**Expected:** derivative -4; loss 4.

**Verify:** Compare the computed values or written argument with derivative -4; loss 4.

## Exercise 2: Check three finite differences

The question is: Use \(h\in\{0.1, 0.01, 0.001\}\) at \(w=0\) and compare each slope with \(-4\).

The quadratic central difference is especially clean. This does not imply every function or every step size achieves the same tolerance.

```python
for h in [0.1, 0.01, 0.001]:
    slope = central(lambda value: (value - 2) ** 2, 0.0, h)
    np.testing.assert_allclose(slope, -4, atol=1e-10, rtol=0)
```

**Expected:** all agree within 1e-10.

**Verify:** Compare the computed values or written argument with all agree within 1e-10.

## Exercise 3: Separate gradient from update

The question is: Use learning rate \(\eta=0.1\) and gradient \(-4\) at \(w=0\).

The update includes direction, step size and old state. Treating the gradient as the parameter would implement a different algorithm.

```python
updated = 0.0 - 0.1 * gradient.item()
np.testing.assert_allclose(updated, 0.4, atol=1e-12, rtol=0)
assert updated != gradient.item()
```

**Expected:** new parameter \(w=0.4\); the supplied gradient is \(-4\).

**Verify:** Compare the computed values or written argument with new parameter \(w=0.4\); the supplied gradient is \(-4\).

## Exercise 4: Inspect a stationary point

The question is: Differentiate the same objective at \(w=2\).

A zero derivative is a numerical result on a connected graph. It must not be confused with a missing gradient path.

```python
optimum = torch.tensor(2.0, dtype=torch.float64, requires_grad=True)
value = (optimum - 2) ** 2
derivative = torch.autograd.grad(value, optimum)[0]
assert value.item() == 0 and derivative.item() == 0
```

**Expected:** gradient 0 and loss 0.

**Verify:** Compare the computed values or written argument with gradient 0 and loss 0.

## Exercise 5: Observe grad-return behavior

The question is: Check that `autograd.grad` did not accumulate into the `leaf.grad` field.

PyTorch offers both returned-gradient and accumulating-backward interfaces. Knowing which one is used prevents stale or missing update state.

```python
assert w.grad is None and gradient.item() == -4
```

**Expected:** `w.grad` is None despite a returned derivative.

**Verify:** Compare the computed values or written argument with `w.grad` is None despite a returned derivative.

## Exercise 6: Reject invalid probes

The question is: Pass \(h=0\), negative h and a function returning infinity to the finite-difference helper.

Validation distinguishes an unusable numerical check from a disagreement with the analytic derivative. Widening a tolerance cannot repair undefined input.

```python
for function, h in [(lambda x: x * x, 0), (lambda x: x * x, -0.1), (lambda x: float("inf"), 0.1)]:
    try:
        central(function, 0.0, h)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid derivative probe accepted")
try:
    central(lambda value: 0.0, float("nan"), 0.1)
except ValueError:
    pass
else:
    raise AssertionError("nonfinite probe point accepted")
```

**Expected:** all raise ValueError.

**Verify:** Compare the computed values or written argument with all raise ValueError.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
