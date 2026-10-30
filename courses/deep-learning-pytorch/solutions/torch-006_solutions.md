# torch-006: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Autograd follows the chain of tensor operations from a scalar objective back to its inputs. Forz=2w, \(a={z}^{2}\), \(\mathrm{loss}={\left(a-1\right)}^{2}\), the derivative multiplies the local sensitivities along that chain. PyTorch builds the graph dynamically during the forward pass and saves values needed for backward. An in-place mutation can invalidate those saved values, so the framework uses version checks and restricts some mutations. A failure is a signal to understand ownership and graph lifetime, not a reason to bypass checks with.data.

Graph state is also temporary. After a normal backward pass, the saved intermediates are released; reusing the same graph for another backward usually requires an explicit retention policy or a fresh forward computation. Most training loops should recompute the forward graph per batch. Nonlinearities such as ReLU introduce points where a derivative convention matters.

**Autograd graph:** The recorded tensor-operation dependencies used for differentiation.

**Saved tensor:** An intermediate value retained because backward needs it.

**In-place hazard:** A mutation that changes data required by a recorded derivative.

## Reading the implementation

Build every intermediate from a requires_grad leaf. autograd.grad(loss, w) composes the chain rule. A direct in-place add on a leaf requiring gradients raises RuntimeError unless performed under a deliberate no_grad update context. Mutating a saved input under no_grad can still make a later backward fail its version check. Use clone when a separate mutable value is needed and recompute the graph after optimizer updates.

## Trace the graph and its saved values

The chain is w→z→a→L, with z=2w, \(a={z}^{2}\) and \(L={\left(a-1\right)}^{2}\). At \(w=1\), the full trace is:

| Operation | Forward value | Immediate derivative |
| --- | --- | --- |
| z=2w | \(z=2\) | \(\frac{\partial z}{\partial w}=2\) |
| \(a={z}^{2}\) | \(a=4\) | da/dz=2z=4 |
| \(L={\left(a-1\right)}^{2}\) | \(L=9\) | dL/da=2(a-1)=6 |

Backward composes sensitivities in reverse dependency order: \(\frac{\partial L}{\partial w}=6\cdot 4\cdot 2=48\). Omitting the inner scale gives 24, even though every forward value remains correct. Changing the inner scale to three gives \(z=3\), \(a=9\), \(L=64\) and derivative \(16\cdot 6\cdot 3=288\). A learning-rate adjustment that hides the missing factor for scale 2 would not repair the algorithm for scale 3.

The scalar expression can also be expanded to \(L=16w^4-8w^2+1\). Its derivative \(64w^3-16w\) equals 48 at one, providing a symbolic check independent of the local-factor table. The finite-difference check recomputes the complete expression at 1+h and 1-h. Holding \(a=4\) fixed while perturbing w would instead probe a constant function with slope zero. Equal forward values at one point do not establish equal dependencies.

For larger tensors, reverse-mode differentiation propagates vector-Jacobian products rather than materializing every possible derivative matrix. A scalar loss supplies the initial sensitivity one; each operation transforms the incoming sensitivity using its saved forward values. This explains why the graph must retain information from the actual forward pass and why asking for derivatives of a nonscalar result requires an explicit upstream-gradient convention.

Consider `objective = value.square()` when value is two. Backward needs the original value to produce derivative four. If code then changes that storage to three before calling backward, the old objective still represents the forward value four, but the saved input has changed. Computing derivative six from the new storage would mix two different states. PyTorch's saved-tensor version checks reject such an invalid sequence rather than silently returning that mixed-state result. [PyTorch 2.9 autograd mechanics](https://docs.pytorch.org/docs/2.9/notes/autograd.html).

Using no_grad around the mutation prevents recording that new operation. It does not restore the saved value or make the earlier graph consistent. A safe ordinary update sequence completes the current derivative computation, updates parameter state at a deliberate boundary, then recomputes the next forward graph. Clone can provide separate mutable storage, but a clone is not a substitute for knowing which value each graph depends on.

After a normal derivative computation, saved intermediates can be released. Keeping a reference to loss does not promise another backward pass can reconstruct those released values. Repeated training usually needs a new forward pass, whereas an algorithm intentionally querying multiple derivatives can request graph retention and accept its memory cost. Do not confuse retaining a graph with accumulating gradients across distinct fresh graphs.

ReLU adds a separate mathematical boundary. At a negative input the derivative is zero; at a positive input it is one. At zero there is no unique classical derivative, and PyTorch chooses zero for backward. The numerical convention is not a graph-disconnection error. It should be recorded explicitly when designing derivative tests rather than judged against a symmetric probe's0.5 as if both were the same object.

## Exercise 1: Trace the chain rule

The question is: Use \(w=1\), \(z=2\cdot w\), \(a=z\cdot z\) and \(\mathrm{loss}={\left(a-1\right)}^{2}\).

The factors are dL/da=2(a-1)=6, da/dz=2z=4 and \(\frac{\partial z}{\partial w}=2\). Multiplying \(6\cdot 4\cdot 2\) gives 48 at the supplied point.

```python
w = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
z = 2 * w
a = z * z
loss = (a - 1) ** 2
gradient = torch.autograd.grad(loss, w)[0]
assert (z.item(), a.item(), loss.item(), gradient.item()) == (2.0, 4.0, 9.0, 48.0)
```

**Expected:** z2, a4, loss 9, gradient 48.

**Verify:** Compare the computed values or written argument with z2, a4, loss 9, gradient 48.

## Exercise 2: Check an independent slope

The question is: Compare the chain derivative with a central difference of the complete scalar expression.

The finite difference treats the entire function as a black box. It can expose an incorrect manual chain factor without reading the graph internals.

```python
h = 1e-5
f = lambda value: ((2 * value) ** 2 - 1) ** 2
numeric = (f(1 + h) - f(1 - h)) / (2 * h)
np.testing.assert_allclose(numeric, 48, atol=1e-5, rtol=0)
```

**Expected:** approximately 48 within 1e-5.

**Verify:** Compare the computed values or written argument with approximately 48 within 1e-5.

## Exercise 3: Observe a leaf mutation guard

The question is: Try an in-place add on a leaf requiring gradients outside no_grad.

The guard prevents an ambiguous modification of a value whose derivative history is being tracked. Optimizer updates use a deliberate state-update boundary instead.

```python
leaf = torch.tensor(1.0, requires_grad=True)
try:
    leaf.add_(1)
except RuntimeError:
    pass
else:
    raise AssertionError("unsafe leaf mutation accepted")
```

**Expected:** RuntimeError.

**Verify:** Compare the computed values or written argument with RuntimeError.

## Exercise 4: Expose saved-value invalidation

The question is: Build \(\mathrm{loss}=x\cdot x\), mutate x under no_grad before backward, and inspect the failure.

no_grad disables recording of the mutation, but it does not make a previously saved tensor immutable or repair the old graph. Recompute after changing state.

```python
value = torch.tensor(2.0, requires_grad=True)
objective = value.square()
with torch.no_grad():
    value.add_(1)
try:
    objective.backward()
except RuntimeError:
    pass
else:
    raise AssertionError("stale saved value accepted")
```

**Expected:** RuntimeError from a changed saved tensor version.

**Verify:** Compare the computed values or written argument with RuntimeError from a changed saved tensor version.

## Exercise 5: Inspect a ReLU convention

The question is: Differentiate ReLU at negative, zero and positive inputs.

PyTorch chooses zero at the kink. A symmetric finite difference at zero would produce one-half, so that point is not a valid smooth-derivative equality test.

```python
points = torch.tensor([-1.0, 0.0, 1.0], requires_grad=True)
torch.relu(points).sum().backward()
torch.testing.assert_close(points.grad, torch.tensor([0.0, 0.0, 1.0]))
```

**Expected:** gradients 0, 0, 1.

**Verify:** Compare the computed values or written argument with gradients 0, 0, 1.

## Exercise 6: Recompute after an update

The question is: Update a scalar under no_grad, then build a fresh quadratic objective and request its derivative.

A new graph uses the new state consistently. Retaining old graphs across updates consumes memory and can create invalid-version errors.

```python
parameter = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
with torch.no_grad():
    parameter.add_(0.5)
fresh = (parameter - 2) ** 2
assert torch.autograd.grad(fresh, parameter)[0].item() == -1
```

**Expected:** at new \(w=1.5\), gradient -1 for \({\left(w-2\right)}^{2}\).

**Verify:** Compare the computed values or written argument with at new \(w=1.5\), gradient -1 for \({\left(w-2\right)}^{2}\).

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
