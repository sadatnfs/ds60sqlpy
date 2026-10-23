# torch-004: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A loss is a numerical objective with a declared unit and denominator. Squared residuals have squared target units. Summing losses makes the objective scale with the number of participating entries; averaging removes that count from the scalar but changes gradient magnitude. PyTorch MSELoss with reduction='mean' averages all tensor elements, not an abstract notion of records inferred from their meaning. If each record has several outputs, those outputs also enter the denominator.

Compare reductions before comparing learning rates or frameworks. Duplicating a batch doubles a sum loss and its gradient but leaves a mean unchanged when every observation is duplicated equally. A metric such as absolute error may be reported beside squared loss, but it is not the same quantity. Masked objectives need a numerator and denominator using the same participation rule; zeroing excluded entries while dividing by padded length changes the objective.

**Reduction:** The rule combining per-entry losses into a scalar.

**Loss unit:** The measurement unit implied by the objective.

**Gradient scale:** The magnitude change induced by objective scaling.

## Reading the implementation

F.mse_loss accepts prediction and target tensors; this course validates exact shape equality before calling it. reduction='none' preserves per-entry losses, 'sum' adds them, and'mean' divides by the number of elements. autograd.grad returns derivatives without accumulating into leaf.grad. Use a fresh forward graph for each independent derivative comparison.

## Exercise 1: Compute residual reductions

The question is: Use residuals[1, -1, 2] against zero targets.

The sum and mean differ only by the known count 3 here. Neither value can be interpreted without its denominator and squared-unit label.

```python
residual=torch.tensor([1.,-1.,2.],dtype=torch.float64); zero=torch.zeros_like(residual)
assert F.mse_loss(residual,zero,reduction='sum').item()==6
assert F.mse_loss(residual,zero,reduction='mean').item()==2
torch.testing.assert_close(F.mse_loss(residual,zero,reduction='none'),torch.tensor([1.,1.,4.],dtype=torch.float64))
```

**Expected:** squared entries1, 1, 4; sum6; mean2.

**Verify:** Compare the computed values or written argument with squared entries1, 1, 4; sum6; mean2.

## Exercise 2: Duplicate the batch

The question is: Repeat every residual twice and compare reductions.

Duplicating observations does not create new information, but it changes a sum objective. This matters when comparing updates across batch sizes.

```python
duplicated=residual.repeat(2)
assert F.mse_loss(duplicated,torch.zeros_like(duplicated),reduction='sum').item()==12
assert F.mse_loss(duplicated,torch.zeros_like(duplicated),reduction='mean').item()==2
```

**Expected:** sum12; mean2.

**Verify:** Compare the computed values or written argument with sum12; mean2.

## Exercise 3: Compare derivative scale

The question is: Differentiate sum and mean squared loss for a fresh3-entry tensor.

The reduction scales every derivative by the same factor. A learning-rate comparison that ignores this can mistake an objective change for optimizer behavior.

```python
a=residual.clone().requires_grad_(); gsum=torch.autograd.grad((a*a).sum(),a)[0]
b=residual.clone().requires_grad_(); gmean=torch.autograd.grad((b*b).mean(),b)[0]
torch.testing.assert_close(gsum,3*gmean,atol=1e-12,rtol=0)
```

**Expected:** sum gradient equals3 times mean gradient.

**Verify:** Compare the computed values or written argument with sum gradient equals3 times mean gradient.

## Exercise 4: Inspect a feature denominator

The question is: Use a2x2 residual matrix of ones and mean reduction.

The framework does not know whether columns are features, tasks or repeated observations. The author must define whether averaging over all entries matches the intended objective.

```python
matrix=torch.ones((2,2),dtype=torch.float64)
assert F.mse_loss(matrix,torch.zeros_like(matrix)).item()==1 and matrix.numel()==4
```

**Expected:** loss1 and4 participating elements.

**Verify:** Compare the computed values or written argument with loss1 and4 participating elements.

## Exercise 5: Mask numerator and denominator together

The question is: Use losses[1, 4, 100] with mask True, True, False.

Excluded targets must not remain in the denominator. Appending more masked entries should leave the result unchanged.

```python
losses=torch.tensor([1.,4.,100.]); mask=torch.tensor([True,True,False])
valid=losses[mask].sum()/mask.sum()
assert valid.item()==2.5 and valid.item()!=5/3
```

**Expected:** valid mean2.5, not5/3.

**Verify:** Compare the computed values or written argument with valid mean2.5, not5/3.

## Exercise 6: Separate a metric from the objective

The question is: Compare mean absolute residual and mean squared residual for[1, -1, 2].

The two measures have different units and emphasize large errors differently. Reporting one does not prove the other was optimized.

```python
np.testing.assert_allclose(residual.abs().mean().item(),4/3,atol=1e-12,rtol=0)
assert residual.square().mean().item()==2
```

**Expected:** MAE4/3; MSE2.

**Verify:** Compare the computed values or written argument with MAE4/3; MSE2.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
