# torch-008: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

One optimizer step is the smallest complete training experiment. Specify inputs, targets, initial weight, dtype, loss reduction, learning rate and optimizer rule. Calculate the forward loss, derive the gradient, apply the update and recompute the loss at the new state. A PyTorch optimizer does not calculate gradients itself: backward populates the parameter.grad fields and optimizer.step consumes them. zero_grad establishes which contributions belong to the next step.

The scalar fixture x = [1, 2, 3], y = 2x, w = 0 and rate 0.1 has an exact oracle. Mean squared loss starts at \(\frac{56}{3}\), the derivative is-\(\frac{56}{3}\), the new weight is \(\frac{28}{15}\), and the new loss is \(\frac{56}{675}\). A mistakenly broadcast column target gives the same initial loss but a different gradient. This is why comparing only a printed initial objective is an inadequate correctness test.

**Optimizer membership:** The exact parameter objects whose gradients an optimizer consumes.

**SGD step:** Subtracting learning rate times the current gradient.

**Independent oracle:** A separately derived expected result for the computation.

## Reading the implementation

Wrap the scalar weight in nn.Parameter with float64. Use an SGD optimizer with momentum 0 and no weight decay. Call zero_grad, set the mean squared residual objective, backward, save the gradient, then step. Use a fresh forward expression for the post-update loss. Validate prediction/target shape equality before allowing a production loss helper to rely on broadcasting.

## Derive the complete scalar training transition

The hypothesis is prediction_i=w x_i for x=[1, 2, 3] and y=2x. With a mean over three paired observations, the objective simplifies to:

`L(w) = (1²+2²+3²)(w-2)²/3 = (14/3)(w-2)²`.

Its derivative is`g(w)=(28/3)(w-2)`. At \(w=0\), the predictions are zeros, residuals[-2, -4, -6], squared errors[4, 16, 36], loss \(\frac{56}{3}\) and gradient-\(\frac{56}{3}\). The input features can remain ordinary constant tensors because the requested derivative is with respect to w. Targets also remain fixed labels rather than state the optimizer is allowed to change.

For learning rateη=1/10, plain SGD gives \(w_{\mathrm{new}}=w-\eta g=\frac{28}{15}\). The new residual is(w_new-2)x=(-2/15)x, so its entries are[-2/15, \(\frac{-4}{15}\), -6/15]. Squaring and averaging gives \(\frac{56}{675}\). The before-loss, gradient, new parameter and after-loss are four separately inspected observations:

| Stage | Weight | Quantity observed |
| --- | --- | --- |
| Forward | 0 | \(L=\frac{56}{3}\) |
| Backward | 0 | stored \(\mathrm{gradient}=\frac{-56}{3}\) |
| Step | \(\frac{28}{15}\) | parameter changed by \(\frac{28}{15}\) |
| New forward | \(\frac{28}{15}\) | \(L=\frac{56}{675}\) |

Backward does not perform the update, and step does not recompute the loss. The old loss tensor still records the earlier forward result after the parameter changes. The fresh Parameter starts with no stored gradient, which makes the first backward unambiguous; repeated independent steps need an explicit clearing policy. The SGD API specifies how momentum, weight decay and other options would change this simpler transition. [PyTorch 2.9 SGD](https://docs.pytorch.org/docs/2.9/generated/torch.optim.SGD.html).

The exact quadratic also permits a stability calculation. Let \(e=w-2\) be the error from the optimum. One update gives \(e_{\mathrm{new}}=\left(1-\frac{28\eta}{3}\right)e\). Repeated full-batch updates contract this error only when \(\left|1-\frac{28\eta}{3}\right|<1\), or \(0<\eta<\frac{3}{14}\). Atη=0.1, the contraction factor is \(\frac{1}{15}\). Atη=0.25, it is-4/3: the parameter crosses the optimum and its error grows. The first weight becomes \(\frac{14}{3}\) and the new loss \(\frac{896}{27}\), larger than the initial \(\frac{56}{3}\) despite a correct derivative.

Changing to a summed objective changes that bound because the gradient is three times larger. This is why learning-rate claims require a declared denominator. The result is exact for this fixed convex scalar objective; it is not a universal neural-network learning-rate rule.

The mistaken column target produces a different objective over every input-target pair. Its mean can be expanded as`L_bad(w)=(14/3)w²-16w+56/3`. At zero, it shares the correct initial loss \(\frac{56}{3}\), but its derivative is-16. Its optimum is \(\frac{12}{7}\) rather than two, and its minimum is \(\frac{104}{21}\) rather than zero. This is a changed statistical pairing, not merely an objective-scale factor. Adjusting the learning rate to disguise the first gradient difference cannot restore the intended optimum.

An audit should therefore check the residual shape and per-record identity before reducing to a scalar. It should then compare the derivative with the independent NumPy probe and verify that the optimizer owns the exact Parameter object whose gradient was computed. Only after those boundaries pass does a longer loop add useful evidence.

## Exercise 1: Calculate the initial loss

The question is: Use float64 x = [1, 2, 3], y = 2x and scalar w = 0.

The three squared residuals are 4, 16, 36. Their sum 56 divided by three defines the objective denominator.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
loss=((w*x-y)**2).mean(); np.testing.assert_allclose(loss.item(),56/3,atol=1e-12,rtol=0)
```

**Expected:** mean squared loss \(\frac{56}{3}\).

**Verify:** Compare the computed values or written argument with mean squared loss \(\frac{56}{3}\).

## Exercise 2: Inspect the gradient before updating

The question is: Back propagate the initial loss and compare with-\(\frac{56}{3}\).

Backward computes derivatives but does not update the parameter. Separating these observations helps diagnose a missing optimizer step.

```python
loss.backward(); np.testing.assert_allclose(w.grad.item(),-56/3,atol=1e-12,rtol=0)
assert w.item()==0
```

**Expected:** gradient-\(\frac{56}{3}\); weight still 0.

**Verify:** Compare the computed values or written argument with gradient-\(\frac{56}{3}\); weight still 0.

## Exercise 3: Apply exactly one SGD update

The question is: Use SGD learning rate 0.1 onw and recompute the objective afterward.

The optimizer consumes the stored gradient. The old loss tensor remains the before-update result, so the new loss requires another forward calculation.

```python
optimizer=torch.optim.SGD([w],lr=.1); optimizer.step()
np.testing.assert_allclose(w.item(),28/15,atol=1e-12,rtol=0)
np.testing.assert_allclose(((w*x-y)**2).mean().item(),56/675,atol=1e-12,rtol=0)
```

**Expected:** w28/15; loss \(\frac{56}{675}\).

**Verify:** Compare the computed values or written argument with w28/15; loss \(\frac{56}{675}\).

## Exercise 4: Expose the broadcast counterexample

The question is: At a fresh w = 0, compare vector predictions with column targets shaped(3, 1).

The result now contains nine pairwise residuals. Equal initial loss is a coincidence of the zero prediction and does not preserve the intended pairing.

```python
wrong=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); broken=((wrong*x-y[:,None])**2).mean(); broken.backward()
np.testing.assert_allclose(broken.item(),56/3,atol=1e-12,rtol=0); assert wrong.grad.item()==-16
```

**Expected:** initial loss still \(\frac{56}{3}\), but gradient-16.

**Verify:** Compare the computed values or written argument with initial loss still \(\frac{56}{3}\), but gradient-16.

## Exercise 5: Check a finite-difference gradient

The question is: Use a plain NumPy scalar objective around \(w=0\) with finite-difference step \(h=0.001\).

The checker does not read the PyTorch gradient buffer. It verifies the complete scalar objective through perturbed values.

```python
values=np.array([1.,2.,3.]); objective=lambda value:np.mean((value*values-2*values)**2); h=.001
slope=(objective(h)-objective(-h))/(2*h)
np.testing.assert_allclose(slope,-56/3,atol=1e-9,rtol=0)
```

**Expected:** slope-\(\frac{56}{3}\) within 1e-9.

**Verify:** Compare the computed values or written argument with slope-\(\frac{56}{3}\) within 1e-9.

## Exercise 6: Clear the consumed gradient

The question is: Call `optimizer.zero_grad(set_to_none=True)` after the step and inspect state.

Clearing derivatives is not undoing the parameter update. It prepares an independent next gradient calculation.

```python
saved=w.item(); optimizer.zero_grad(set_to_none=True)
assert w.grad is None and w.item()==saved
```

**Expected:** `w.grad` None; updated weight unchanged.

**Verify:** Compare the computed values or written argument with `w.grad` None; updated weight unchanged.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
