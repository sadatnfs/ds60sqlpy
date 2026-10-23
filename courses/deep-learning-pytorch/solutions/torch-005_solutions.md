# torch-005: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A derivative measures local sensitivity:how much a function changes for a small input change. It is not itself a new parameter value. Gradient descent combines the derivative with a learning rate and a subtraction rule. PyTorch tracks operations involving tensors with requires_grad=True and can calculate a derivative through autograd.grad. A central finite difference estimates the same slope by evaluating the function at nearby inputs, providing an independent numerical check.

Finite differences involve a tradeoff:large steps measure a wider region, while extremely small steps lose precision through subtract iv e cancellation. Float64 is useful for this small diagnostic. At a nondifferentiable kink, a framework's chosen subgradient convention need not equal a symmetric finite difference. This lesson uses a smooth quadratic so the expected derivative is exact and the comparison is interpretable.

**Derivative:** The local rate of change of a function.

**Finite difference:** A numerical slope estimate from nearby function evaluations.

**Learning rate:** A multiplier converting a gradient into an update magnitude.

## Reading the implementation

Forf(w)=(w-2)^2, the analytic derivative is2(w-2). Construct a scalar float64tensor with requires_grad=True, calculate f, and request autograd.grad(f, w). The returned tensor does not automatically populate w.grad. A central difference uses(f(w+h)-f(w-h))/(2h). Validate positive finite h and finite function values before comparing.

## Exercise 1: Derive a scalar slope

The question is: Differentiate (w-2)**2 at w=0 using autograd.grad.

The analytic derivative provides an oracle independent of autograd. The negative sign means increasing w locally decreases the loss.

```python
w=torch.tensor(0.,dtype=torch.float64,requires_grad=True); loss=(w-2)**2
gradient=torch.autograd.grad(loss,w)[0]
assert gradient.item()==-4 and loss.item()==4
```

**Expected:** derivative -4; loss4.

**Verify:** Compare the computed values or written argument with derivative -4; loss4.

## Exercise 2: Check three finite differences

The question is: Useh.1, .01, .001 atw0 and compare each slope with-4.

The quadratic central difference is especially clean. This does not imply every function or every step size achieves the same tolerance.

```python
for h in [.1,.01,.001]:
    slope=central(lambda value:(value-2)**2,0.,h)
    np.testing.assert_allclose(slope,-4,atol=1e-10,rtol=0)
```

**Expected:** all agree within1e-10.

**Verify:** Compare the computed values or written argument with all agree within1e-10.

## Exercise 3: Separate gradient from update

The question is: Use learning rate.1 and gradient-4 from w0.

The update includes direction, step size and old state. Treating the gradient as the parameter would implement a different algorithm.

```python
updated=0.-.1*gradient.item()
np.testing.assert_allclose(updated,.4,atol=1e-12,rtol=0)
assert updated!=gradient.item()
```

**Expected:** neww.4, not-4.

**Verify:** Compare the computed values or written argument with neww.4, not-4.

## Exercise 4: Inspect a stationary point

The question is: Differentiate the same objective atw2.

A zero derivative is a numerical result on a connected graph. It must not be confused with a missing gradient path.

```python
optimum=torch.tensor(2.,dtype=torch.float64,requires_grad=True)
value=(optimum-2)**2; derivative=torch.autograd.grad(value,optimum)[0]
assert value.item()==0 and derivative.item()==0
```

**Expected:** gradient0 and loss0.

**Verify:** Compare the computed values or written argument with gradient0 and loss0.

## Exercise 5: Observe grad-return behavior

The question is: Check that autograd.grad did not accumulate into the leaf.grad field.

PyTorch offers both returned-gradient and accumulating-backward interfaces. Knowing which one is used prevents stale or missing update state.

```python
assert w.grad is None and gradient.item()==-4
```

**Expected:** w.grad is None despite a returned derivative.

**Verify:** Compare the computed values or written argument with w.grad is None despite a returned derivative.

## Exercise 6: Reject invalid probes

The question is: Pass h0, negative h and a function returning infinity to the finite-difference helper.

Validation distinguishes an unusable numerical check from a disagreement with the analytic derivative. Widening a tolerance cannot repair undefined input.

```python
for function,h in [(lambda x:x*x,0),(lambda x:x*x,-.1),(lambda x:float('inf'),.1)]:
    try: central(function,0.,h)
    except ValueError: pass
    else: raise AssertionError('invalid derivative probe accepted')
```

**Expected:** all raise ValueError.

**Verify:** Compare the computed values or written argument with all raise ValueError.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
