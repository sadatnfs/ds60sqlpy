# torch-008: explanatory solutions

Open these answers only after attempting One optimizer step you can audit yourself. They reuse the guide's literal inputs, starting from Example A, Calculate the initial loss, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Optimizer membership, SGD step, Independent oracle. After a pass, choose a new input for exercise 6, Clear the consumed gradient, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

One optimizer step is the smallest complete training experiment. Specify inputs, targets, initial weight, dtype, loss reduction, learning rate and optimizer rule. Calculate the forward loss, derive the gradient, apply the update and recompute the loss at the new state. A PyTorch optimizer does not calculate gradients itself: backward populates the parameter.grad fields and optimizer.step consumes them. zero_grad establishes which contributions belong to the next step.

The scalar fixture x = [1, 2, 3], y = 2x, w = 0 and rate 0.1 has an exact oracle. Mean squared loss starts at \(\frac{56}{3}\), the derivative is -\(\frac{56}{3}\), the new weight is \(\frac{28}{15}\), and the new loss is \(\frac{56}{675}\). A mistakenly broadcast column target gives the same initial loss but a different gradient. This is why comparing only a printed initial objective is an inadequate correctness test.

**Optimizer membership:** The exact parameter objects whose gradients an optimizer consumes.

**SGD step:** Subtracting learning rate times the current gradient.

**Independent oracle:** A separately derived expected result for the computation.

## Reading the implementation

Wrap the scalar weight in nn.Parameter with float64. Use an SGD optimizer with momentum 0 and no weight decay. Call zero_grad, set the mean squared residual objective, backward, save the gradient, then step. Use a fresh forward expression for the post-update loss. Validate prediction/target shape equality before allowing a production loss helper to rely on broadcasting.

## Derive the complete scalar training transition

The hypothesis is prediction_i=w x_i for x=[1, 2, 3] and y=2x. With a mean over three paired observations, the objective simplifies to:

`L(w) = (1²+2²+3²)(w-2)²/3 = (14/3)(w-2)²`.

Its derivative is`g(w)=(28/3)(w-2)`. At \(w=0\), the predictions are zeros, residuals [-2, -4, -6], squared errors [4, 16, 36], loss \(\frac{56}{3}\) and gradient -\(\frac{56}{3}\). The input features can remain ordinary constant tensors because the requested derivative is with respect to w. Targets also remain fixed labels rather than state the optimizer is allowed to change.

For learning rateη=1/10, plain SGD gives \(w_{\mathrm{new}}=w-\eta g=\frac{28}{15}\). The new residual is (w_new-2)x=(-2/15)x, so its entries are [-2/15, \(\frac{-4}{15}\), -6/15]. Squaring and averaging gives \(\frac{56}{675}\). The before-loss, gradient, new parameter and after-loss are four separately inspected observations:

| Stage | Weight | Quantity observed |
| --- | --- | --- |
| Forward | 0 | \(L=\frac{56}{3}\) |
| Backward | 0 | stored \(\mathrm{gradient}=\frac{-56}{3}\) |
| Step | \(\frac{28}{15}\) | parameter changed by \(\frac{28}{15}\) |
| New forward | \(\frac{28}{15}\) | \(L=\frac{56}{675}\) |

Backward does not perform the update, and step does not recompute the loss. The old loss tensor still records the earlier forward result after the parameter changes. The fresh Parameter starts with no stored gradient, which makes the first backward unambiguous; repeated independent steps need an explicit clearing policy. The SGD API specifies how momentum, weight decay and other options would change this simpler transition. [PyTorch 2.9 SGD](https://docs.pytorch.org/docs/2.9/generated/torch.optim.SGD.html).

The exact quadratic also permits a stability calculation. Let \(e=w-2\) be the error from the optimum. One update gives \(e_{\mathrm{new}}=\left(1-\frac{28\eta}{3}\right)e\). Repeated full-batch updates contract this error only when \(\left|1-\frac{28\eta}{3}\right|<1\), or \(0<\eta<\frac{3}{14}\). Atη=0.1, the contraction factor is \(\frac{1}{15}\). Atη=0.25, it is -4/3: the parameter crosses the optimum and its error grows. The first weight becomes \(\frac{14}{3}\) and the new loss \(\frac{896}{27}\), larger than the initial \(\frac{56}{3}\) despite a correct derivative.

Changing to a summed objective changes that bound because the gradient is three times larger. This is why learning-rate claims require a declared denominator. The result is exact for this fixed convex scalar objective; it is not a universal neural-network learning-rate rule.

The mistaken column target produces a different objective over every input-target pair. Its mean can be expanded as`L_bad(w)=(14/3)w²-16w+56/3`. At zero, it shares the correct initial loss \(\frac{56}{3}\), but its derivative is -16. Its optimum is \(\frac{12}{7}\) rather than two, and its minimum is \(\frac{104}{21}\) rather than zero. This is a changed statistical pairing, not merely an objective-scale factor. Adjusting the learning rate to disguise the first gradient difference cannot restore the intended optimum.

An audit should therefore check the residual shape and per-record identity before reducing to a scalar. It should then compare the derivative with the independent NumPy probe and verify that the optimizer owns the exact Parameter object whose gradient was computed. Only after those boundaries pass does a longer loop add useful evidence.

## Exercise 1: Compute a new initial loss

The question is: Use float64 x = 1, 2, targets y = 3x and scalar w = 0, and calculate the mean squared loss.

The residuals are -3 and -6, so the mean of 9 and 36 is 22.5.

```python
xs = torch.tensor([1.0, 2.0], dtype=torch.float64)
ys = 3 * xs
ws = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
objective = ((ws * xs - ys) ** 2).mean()
np.testing.assert_allclose(objective.item(), 22.5, atol=1e-12, rtol=0)
```

**Expected:** loss 22.5.

**Verify:** In a fresh process, the exercise checks confirm `objective.item()` matches `22.5` within 1e-12.

## Exercise 2: Predict the gradient before stepping

The question is: Backpropagate the new loss and compare the gradient with your hand calculation before any update.

The derivative is the mean of 2(wx-y)x, here the mean of -6 and -24.

```python
objective.backward()
np.testing.assert_allclose(ws.grad.item(), -15, atol=1e-12, rtol=0)
assert ws.item() == 0
```

**Expected:** gradient -15; w still 0.

**Verify:** In a fresh process, the exercise checks confirm `ws.grad.item()` matches `-15` within 1e-12 and `ws.item() == 0`.

## Exercise 3: Apply one step with a new rate

The question is: Take one SGD step with learning rate 0.05 and recompute the loss.

The step moves w by 0.05*15; the residual factor becomes 0.75-3=-2.25, and 2.25 squared times the mean of x squared (2.5) gives 12.65625.

```python
sgd = torch.optim.SGD([ws], lr=0.05)
sgd.step()
np.testing.assert_allclose(ws.item(), 0.75, atol=1e-12, rtol=0)
np.testing.assert_allclose(((ws * xs - ys) ** 2).mean().item(), 12.65625, atol=1e-12, rtol=0)
```

**Expected:** w = 0.75; loss 12.65625.

**Verify:** In a fresh process, the exercise checks confirm `ws.item()` matches `0.75` within 1e-12 and `((ws * xs - ys) ** 2).mean().item()` matches `12.65625` within 1e-12.

## Exercise 4: Expose the broadcast counterexample

The question is: At a fresh w = 0, compare vector predictions with column targets shaped (3, 1).

The result now contains nine pairwise residuals. Equal initial loss is a coincidence of the zero prediction and does not preserve the intended pairing.

```python
wrong = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
broken = ((wrong * x - y[:, None]) ** 2).mean()
broken.backward()
np.testing.assert_allclose(broken.item(), 56 / 3, atol=1e-12, rtol=0)
assert wrong.grad.item() == -16
```

**Expected:** initial loss still \(\frac{56}{3}\), but gradient -16.

**Verify:** In a fresh process, the exercise checks confirm `broken.item()` matches `56 / 3` within 1e-12 and `wrong.grad.item() == -16`.

## Exercise 5: Check a finite-difference gradient

The question is: Use a plain NumPy scalar objective around \(w=0\) with finite-difference step \(h=0.001\).

The checker does not read the PyTorch gradient buffer. It verifies the complete scalar objective through perturbed values.

```python
values = np.array([1.0, 2.0, 3.0])
objective = lambda value: np.mean((value * values - 2 * values) ** 2)
h = 0.001
slope = (objective(h) - objective(-h)) / (2 * h)
np.testing.assert_allclose(slope, -56 / 3, atol=1e-9, rtol=0)
```

**Expected:** slope -\(\frac{56}{3}\) within 1e-9.

**Verify:** In a fresh process, the exercise checks confirm `slope` matches `-56 / 3` within 1e-09.

## Exercise 6: Clear the consumed gradient

The question is: Call `optimizer.zero_grad(set_to_none=True)` after the step and inspect state.

Clearing derivatives is not undoing the parameter update. It prepares an independent next gradient calculation.

```python
saved = w.item()
optimizer.zero_grad(set_to_none=True)
assert w.grad is None and w.item() == saved
```

**Expected:** `w.grad` None; updated weight unchanged.

**Verify:** In a fresh process, the exercise checks confirm `w.grad is None` and `w.item() == saved`.

