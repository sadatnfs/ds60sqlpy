# torch-008: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

One optimizer step is the smallest complete training experiment. Specify inputs, targets, initial weight, dtype, loss reduction, learning rate and optimizer rule. Calculate the forward loss, derive the gradient, apply the update and recompute the loss at the new state. A PyTorch optimizer does not calculate gradients itself:backward populates the parameter.grad fields and optimizer.step consumes them. zero_grad establishes which contributions belong to the next step.

The scalar fixture x1, 2, 3, y2 x, w0 and rate.1 has an exact oracle. Mean squared loss starts at56/3, the derivative is-56/3, the new weight is28/15, and the new loss is56/675. A mistaken l y broadcast column target gives the same initial loss but a different gradient. This is why comparing only a printed initial objective is an inadequate correctness test.

**Optimizer membership:** The exact parameter objects whose gradients an optimizer consumes.

**SGD step:** Subtracting learning rate times the current gradient.

**Independent oracle:** A separately derived expected result for the computation.

## Reading the implementation

Wrap the scalar weight innn.Parameter with float64. Use an SGD optimizer with momentum0 and no weight decay. Call zero_grad, set the mean squared residual objective, backward, save the gradient, then step. Use a fresh forward expression for the post-update loss. Validate prediction/target shape equality before allowing a production loss helper to rely on broadcasting.

## Exercise 1: Calculate the initial loss

The question is: Use float64 x1, 2, 3, y2 x and scalar w0.

The three squared residuals are4, 16, 36. Their sum56 divided by three defines the objective denominator.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
loss=((w*x-y)**2).mean(); np.testing.assert_allclose(loss.item(),56/3,atol=1e-12,rtol=0)
```

**Expected:** mean squared loss56/3.

**Verify:** Compare the computed values or written argument with mean squared loss56/3.

## Exercise 2: Inspect the gradient before updating

The question is: Back propagate the initial loss and compare with-56/3.

Backward computes derivatives but does not update the parameter. Separating these observations helps diagnose a missing optimizer step.

```python
loss.backward(); np.testing.assert_allclose(w.grad.item(),-56/3,atol=1e-12,rtol=0)
assert w.item()==0
```

**Expected:** gradient-56/3; weight still0.

**Verify:** Compare the computed values or written argument with gradient-56/3; weight still0.

## Exercise 3: Apply exactly one SGD update

The question is: Use SGD learning rate.1 onw and recompute the objective afterward.

The optimizer consumes the stored gradient. The old loss tensor remains the before-update result, so the new loss requires another forward calculation.

```python
optimizer=torch.optim.SGD([w],lr=.1); optimizer.step()
np.testing.assert_allclose(w.item(),28/15,atol=1e-12,rtol=0)
np.testing.assert_allclose(((w*x-y)**2).mean().item(),56/675,atol=1e-12,rtol=0)
```

**Expected:** w28/15; loss56/675.

**Verify:** Compare the computed values or written argument with w28/15; loss56/675.

## Exercise 4: Expose the broadcast counterexample

The question is: At a fresh w0, compare vector predictions with column targets shaped(3, 1).

The result now contains nine pairwise residuals. Equal initial loss is a coincidence of the zero prediction and does not preserve the intended pairing.

```python
wrong=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); broken=((wrong*x-y[:,None])**2).mean(); broken.backward()
np.testing.assert_allclose(broken.item(),56/3,atol=1e-12,rtol=0); assert wrong.grad.item()==-16
```

**Expected:** initial loss still56/3, but gradient-16.

**Verify:** Compare the computed values or written argument with initial loss still56/3, but gradient-16.

## Exercise 5: Check a finite-difference gradient

The question is: Use a plain NumPy scalar objective around w0 with h.001.

The checker does not read the PyTorch gradient buffer. It verifies the complete scalar objective through perturbed values.

```python
values=np.array([1.,2.,3.]); objective=lambda value:np.mean((value*values-2*values)**2); h=.001
slope=(objective(h)-objective(-h))/(2*h)
np.testing.assert_allclose(slope,-56/3,atol=1e-9,rtol=0)
```

**Expected:** slope-56/3 within1e-9.

**Verify:** Compare the computed values or written argument with slope-56/3 within1e-9.

## Exercise 6: Clear the consumed gradient

The question is: Call optimizer.zero_grad(set_to_none=True) after the step and inspect state.

Clearing derivatives is not undo in g the parameter update. It prepares an independent next gradient calculation.

```python
saved=w.item(); optimizer.zero_grad(set_to_none=True)
assert w.grad is None and w.item()==saved
```

**Expected:** w.grad None; updated weight unchanged.

**Verify:** Compare the computed values or written argument with w.grad None; updated weight unchanged.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
