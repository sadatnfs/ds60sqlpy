# torch-006: explanatory solutions

Open these answers only after attempting Autograd graphs, the chain rule and in-place hazards yourself. They reuse the guide's literal inputs, starting from Example A, Trace the chain rule, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Autograd graph, Saved tensor, In-place hazard. After a pass, choose a new input for exercise 6, Recompute after an update, without looking.

## Mechanism review

Autograd follows the chain of tensor operations from a scalar objective back to its inputs. Forz=2w, \(a={z}^{2}\), \(\mathrm{loss}={\left(a-1\right)}^{2}\), the derivative multiplies the local sensitivities along that chain. PyTorch builds the graph dynamically during the forward pass and saves values needed for backward. An in-place mutation can invalidate those saved values, so the framework uses version checks and restricts some mutations. A failure is a signal to understand ownership and graph lifetime, not a reason to bypass checks with .data.

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

ReLU adds a separate mathematical boundary. At a negative input the derivative is zero; at a positive input it is one. At zero there is no unique classical derivative, and PyTorch chooses zero for backward. The numerical convention is not a graph-disconnection error. It should be recorded explicitly when designing derivative tests rather than judged against a symmetric probe's 0.5 as if both were the same object.

## Exercise 1: Trace the chain at a new point

The question is: Use w=2, \(z=2\cdot w\), \(a=z\cdot z\) and \(\mathrm{loss}={\left(a-1\right)}^{2}\), and predict each intermediate value and dloss/dw.

The local factors are 2(a-1)=30, 2z=8 and \(\frac{\partial z}{\partial w}=2\), so the chain gives 30*8*2=480.

```python
w2 = torch.tensor(2.0, dtype=torch.float64, requires_grad=True)
z2 = 2 * w2
a2 = z2 * z2
loss2 = (a2 - 1) ** 2
assert (z2.item(), a2.item(), loss2.item()) == (4.0, 16.0, 225.0) and torch.autograd.grad(
    loss2, w2
)[0].item() == 480
```

**Expected:** z = 4, a = 16, loss 225, gradient 480.

**Verify:** In a fresh process, the exercise checks confirm `(z2.item(), a2.item(), loss2.item()) == (4.0, 16.0, 225.0)` and `torch.autograd.grad(loss2, w2)[0].item() == 480`.

## Exercise 2: Check the new slope numerically

The question is: Compare 480 with a central difference of ((2w)**2-1)**2 at w=2 using h=1e-5.

For this quartic the truncation error is about h**2 times the third derivative 768 divided by 6, far below the tolerance.

```python
step = 1e-5
quartic = lambda value: ((2 * value) ** 2 - 1) ** 2
np.testing.assert_allclose(
    (quartic(2 + step) - quartic(2 - step)) / (2 * step), 480, atol=1e-6, rtol=0
)
```

**Expected:** the central difference agrees with 480 within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `(quartic(2 + step) - quartic(2 - step)) / (2 * step)` matches `480` within 1e-06.

## Exercise 3: Update a leaf under no_grad

The question is: Repeat the in-place add on a leaf that requires gradients, but inside torch.no_grad().

Optimizers update parameters exactly this way: the mutation is not recorded in a graph, so autograd allows it.

```python
guarded = torch.tensor(1.0, requires_grad=True)
with torch.no_grad():
    guarded.add_(1)
assert guarded.item() == 2 and guarded.requires_grad and guarded.is_leaf
```

**Expected:** the update succeeds; the value is 2 and the tensor is still a leaf that requires gradients.

**Verify:** In a fresh process, the exercise checks confirm `guarded.item() == 2`, `guarded.requires_grad` and `guarded.is_leaf`.

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

**Verify:** In a fresh process, the exercise checks confirm `objective.backward()` raises `RuntimeError`.

## Exercise 5: Inspect a ReLU convention

The question is: Differentiate ReLU at negative, zero and positive inputs.

PyTorch chooses zero at the kink. A symmetric finite difference at zero would produce one-half, so that point is not a valid smooth-derivative equality test.

```python
points = torch.tensor([-1.0, 0.0, 1.0], requires_grad=True)
torch.relu(points).sum().backward()
torch.testing.assert_close(points.grad, torch.tensor([0.0, 0.0, 1.0]))
```

**Expected:** gradients 0, 0, 1.

**Verify:** In a fresh process, the exercise checks confirm `points.grad` matches `torch.tensor([0.0, 0.0, 1.0])`.

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

**Verify:** In a fresh process, the exercise checks confirm `torch.autograd.grad(fresh, parameter)[0].item() == -1`.

## Review after comparison

Repeat exercise 4, Expose saved-value invalidation, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Inspect a ReLU convention, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
