# torch-006: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Autograd follows the chain of tensor operations from a scalar objective back to its inputs. Forz=2w, a=z², loss=(a-1)², the derivative multiplies the local sensitivities along that chain. PyTorch builds the graph dynamically during the forward pass and saves values needed for backward. An in-place mutation can invalidate those saved values, so the framework uses version checks and restricts some mutations. A failure is a signal to understand ownership and graph lifetime, not a reason to bypass checks with.data.

Graph state is also temporary. After a normal backward pass, the saved intermediates are released; reusing the same graph for another backward usually requires an explicit retention policy or a fresh forward computation. Most training loops should recompute the forward graph per batch. Nonlinearities such as ReLU introduce points where a derivative convention matters.

**Autograd graph:** The recorded tensor-operation dependencies used for differentiation.

**Saved tensor:** An intermediate value retained because backward needs it.

**In-place hazard:** A mutation that changes data required by a recorded derivative.

## Reading the implementation

Build every intermediate from a requires_grad leaf. autograd.grad(loss, w) composes the chain rule. A direct in-place add on a leaf requiring gradients raises RuntimeError unless performed under a deliberate no_grad update context. Mutating a saved input under no_grad can still make a later backward fail its version check. Use clone when a separate mutable value is needed and recompute the graph after optimizer updates.

## Exercise 1: Trace the chain rule

The question is: Use w=1, z=2*w, a=z*z and loss=(a-1)**2.

The factors are2(loss inner), 2z and2 from the affine input, with the outer residual included. Multiplying them gives48 at the supplied point.

```python
w=torch.tensor(1.,dtype=torch.float64,requires_grad=True); z=2*w; a=z*z; loss=(a-1)**2
gradient=torch.autograd.grad(loss,w)[0]
assert (z.item(),a.item(),loss.item(),gradient.item())==(2.,4.,9.,48.)
```

**Expected:** z2, a4, loss9, gradient48.

**Verify:** Compare the computed values or written argument with z2, a4, loss9, gradient48.

## Exercise 2: Check an independent slope

The question is: Compare the chain derivative with a central difference of the complete scalar expression.

The finite difference treats the entire function as a black box. It can expose an incorrect manual chain factor without reading the graph internal s.

```python
h=1e-5; f=lambda value:((2*value)**2-1)**2
numeric=(f(1+h)-f(1-h))/(2*h)
np.testing.assert_allclose(numeric,48,atol=1e-5,rtol=0)
```

**Expected:** approximately48 within1e-5.

**Verify:** Compare the computed values or written argument with approximately48 within1e-5.

## Exercise 3: Observe a leaf mutation guard

The question is: Try an in-place add on a leaf requiring gradients outside no_grad.

The guard prevents an ambiguous modification of a value whose derivative history is being tracked. Optimizer updates use a deliberate state-update boundary instead.

```python
leaf=torch.tensor(1.,requires_grad=True)
try: leaf.add_(1)
except RuntimeError: pass
else: raise AssertionError('unsafe leaf mutation accepted')
```

**Expected:** RuntimeError.

**Verify:** Compare the computed values or written argument with RuntimeError.

## Exercise 4: Expose saved-value invalidation

The question is: Build loss=x*x, mutate x under no_grad before backward, and inspect the failure.

no_grad disables recording of the mutation, but it does not make a previously saved tensor immutable or repair the old graph. Recompute after changing state.

```python
value=torch.tensor(2.,requires_grad=True); objective=value.square()
with torch.no_grad(): value.add_(1)
try: objective.backward()
except RuntimeError: pass
else: raise AssertionError('stale saved value accepted')
```

**Expected:** RuntimeError from a changed saved tensor version.

**Verify:** Compare the computed values or written argument with RuntimeError from a changed saved tensor version.

## Exercise 5: Inspect a ReLU convention

The question is: Differentiate ReLU at negative, zero and positive inputs.

PyTorch chooses zero at the kink. A symmetric finite difference at zero would produce one-half, so that point is not a valid smooth-derivative equality test.

```python
points=torch.tensor([-1.,0.,1.],requires_grad=True); torch.relu(points).sum().backward()
torch.testing.assert_close(points.grad,torch.tensor([0.,0.,1.]))
```

**Expected:** gradients0, 0, 1.

**Verify:** Compare the computed values or written argument with gradients0, 0, 1.

## Exercise 6: Recompute after an update

The question is: Update a scalar under no_grad, then build a fresh quadratic objective and request its derivative.

A new graph uses the new state consistently. Retaining old graphs across updates consumes memory and can create invalid-version errors.

```python
parameter=torch.tensor(1.,dtype=torch.float64,requires_grad=True)
with torch.no_grad(): parameter.add_(.5)
fresh=(parameter-2)**2
assert torch.autograd.grad(fresh,parameter)[0].item()==-1
```

**Expected:** at new w=1.5, gradient -1 for (w-2)**2.

**Verify:** Compare the computed values or written argument with at new w=1.5, gradient -1 for (w-2)**2.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
