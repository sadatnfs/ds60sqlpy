# torch-004: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A loss is a numerical objective with a declared unit and denominator. Squared residuals have squared target units. Summing losses makes the objective scale with the number of participating entries; averaging removes that count from the scalar but changes gradient magnitude. PyTorch MSELoss with reduction='mean' averages all tensor elements, not an abstract notion of records inferred from their meaning. If each record has several outputs, those outputs also enter the denominator.

Compare reductions before comparing learning rates or frameworks. Duplicating a batch doubles a sum loss and its gradient but leaves a mean unchanged when every observation is duplicated equally. A metric such as absolute error may be reported beside squared loss, but it is not the same quantity. Masked objectives need a numerator and denominator using the same participation rule; zeroing excluded entries while dividing by padded length changes the objective.

**Reduction:** The rule combining per-entry losses into a scalar.

**Loss unit:** The measurement unit implied by the objective.

**Gradient scale:** The magnitude change induced by objective scaling.

## Reading the implementation

F.mse_loss accepts prediction and target tensors; a paired-record application should validate exact shape equality before calling it; these literal fixtures construct matching shapes. reduction='none' preserves per-entry losses, 'sum' adds them, and'mean' divides by the number of elements. autograd.grad returns derivatives without accumulating into leaf.grad. Use a fresh forward graph for each independent derivative comparison.

## The denominator determines the gradient

For predictions and targets with identical shape (B, D), let \(r_{bd}=\mathrm{prediction}_{bd}-\mathrm{target}_{bd}\). The squared-error sum is \(S=\sum_b\sum_d r_{bd}^2\). PyTorch's mean MSE divides by B×D, so \(L=\frac{S}{BD}\). Its derivative with respect to each prediction is \(\frac{2r_{bd}}{BD}\). The sum objective instead gives 2 r_bd. This is why changing a reduction changes every gradient even when the forward residuals are identical. [PyTorch 2.9 MSELoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MSELoss.html).

For the residual vector [1, -1, 2], \(S=6\) and \(N=3\). The sum gradient is [2, -2, 4], while the mean gradient is [\(\frac{2}{3}\), \(\frac{-2}{3}\), \(\frac{4}{3}\)]. Duplicating every record doubles the sum and duplicates its derivative contributions. The mean objective remains two because both numerator and denominator double. This argument assumes equal replication of all participating entries; selectively repeating hard examples changes their weighting.

A two-output example makes the semantic unit visible. WithB=2, \(D=2\) and all residuals equal to one, the element mean is one, the total sum is four, and the mean of per-example feature sums is two. The first objective gives each scalar derivative 0.5; the last gives each scalar derivative 1. Both can be mathematically legitimate, but they encode different scaling. A framework cannot infer which one the application intended from the word mean.

Masking must use the same participation rule in the numerator and denominator. Keeping only the first two residuals gives numerator 2, count 2 and loss 1. Zeroing the third contribution and then averaging the original three positions gives \(\frac{2}{3}\). The valid mean gradient for the retained residuals is [1, -1]; dividing by the padded length shrinks it to [\(\frac{2}{3}\), \(\frac{-2}{3}\)]. Padding can therefore change both reported quality and training updates without adding any new observation.

An all-false mask is not the same as two accepted residuals equal to zero. The former has no defined mean denominator; the latter has a valid zero loss. Decide whether the surrounding pipeline should reject an empty objective or skip an update under an explicit policy. Silently calling it a perfect batch hides a missing-data condition.

Group weighting provides another counterexample. If one group contains residual [2] and another contains [0, 0, 0], the all-record MSE is \(\frac{4}{4}=1\). The unweighted mean of group MSEs is (4+0)/2=2. The correct choice depends on whether equal influence belongs to observations or groups. Accumulation and distributed-gradient chapters return to this denominator problem when batch sizes differ.

Finally, loss and evaluation metric need not rank candidates the same way. Residuals [0, 0, 4] have MAE \(\frac{4}{3}\) and MSE \(\frac{16}{3}\); residuals [2, 2, 2] have MAE 2 and MSE 4. Squared error prefers the second candidate because it penalizes the large miss more strongly, while absolute error prefers the first. State the objective and error costs before seeing the ranking.

## Exercise 1: Reduce a new residual vector

The question is: Use residuals [3, 0, -1, 2] against zero targets and compute the sum and mean squared reductions.

The sum adds the four squares; the mean divides that sum by the four participating entries.

```python
fresh = torch.tensor([3.0, 0.0, -1.0, 2.0], dtype=torch.float64)
zeros = torch.zeros_like(fresh)
assert (
    F.mse_loss(fresh, zeros, reduction="sum").item() == 14
    and F.mse_loss(fresh, zeros, reduction="mean").item() == 3.5
)
```

**Expected:** squared entries 9, 0, 1, 4; sum 14; mean 3.5.

**Verify:** In a fresh process, the exercise checks confirm `F.mse_loss(fresh, zeros, reduction='sum').item() == 14` and `F.mse_loss(fresh, zeros, reduction='mean').item() == 3.5`.

## Exercise 2: Predict the effect of an appended zero

The question is: Append one zero residual to the same vector and recompute both reductions before running them.

A zero entry adds nothing to the numerator but still counts in the mean's denominator, which is why padding must be masked.

```python
padded = torch.cat([fresh, torch.zeros(1, dtype=torch.float64)])
assert F.mse_loss(padded, torch.zeros_like(padded), reduction="sum").item() == 14
np.testing.assert_allclose(
    F.mse_loss(padded, torch.zeros_like(padded), reduction="mean").item(), 2.8, atol=1e-12, rtol=0
)
```

**Expected:** sum stays 14; mean falls to 2.8 because the denominator becomes 5.

**Verify:** In a fresh process, the exercise checks confirm `F.mse_loss(padded, torch.zeros_like(padded), reduction='sum').item() == 14` and `F.mse_loss(padded, torch.zeros_like(padded), reduction='mean').item()` matches `2.8` within 1e-12.

## Exercise 3: Compare gradient scale for four entries

The question is: Differentiate the sum and the mean of squares for a fresh copy of [3, 0, -1, 2].

Each derivative of a square is 2r; the mean divides every component by the entry count 4.

```python
c = fresh.clone().requires_grad_()
total_grad = torch.autograd.grad((c * c).sum(), c)[0]
d = fresh.clone().requires_grad_()
mean_grad = torch.autograd.grad((d * d).mean(), d)[0]
torch.testing.assert_close(
    total_grad, torch.tensor([6.0, 0.0, -2.0, 4.0], dtype=torch.float64), atol=1e-12, rtol=0
)
torch.testing.assert_close(total_grad, 4 * mean_grad, atol=1e-12, rtol=0)
```

**Expected:** sum gradient [6, 0, -2, 4]; it equals 4 times the mean gradient.

**Verify:** In a fresh process, the exercise checks confirm `total_grad` matches `torch.tensor([6.0, 0.0, -2.0, 4.0], dtype=torch.float64)` within 1e-12 and `total_grad` matches `4 * mean_grad` within 1e-12.

## Exercise 4: Inspect a feature denominator

The question is: Use a 2-by-2 residual matrix of ones and mean reduction.

The framework does not know whether columns are features, tasks or repeated observations. The author must define whether averaging over all entries matches the intended objective.

```python
matrix = torch.ones((2, 2), dtype=torch.float64)
assert F.mse_loss(matrix, torch.zeros_like(matrix)).item() == 1 and matrix.numel() == 4
```

**Expected:** loss 1 and 4 participating elements.

**Verify:** In a fresh process, the exercise checks confirm `F.mse_loss(matrix, torch.zeros_like(matrix)).item() == 1` and `matrix.numel() == 4`.

## Exercise 5: Mask numerator and denominator together

The question is: Use losses [1, 4, 100] with mask True, True, False.

Excluded targets must not remain in the denominator. Appending more masked entries should leave the result unchanged.

```python
losses = torch.tensor([1.0, 4.0, 100.0])
mask = torch.tensor([True, True, False])
valid = losses[mask].sum() / mask.sum()
assert valid.item() == 2.5 and valid.item() != 5 / 3
```

**Expected:** valid mean 2.5, not \(\frac{5}{3}\).

**Verify:** In a fresh process, the exercise checks confirm `valid.item() == 2.5` and `valid.item() != 5 / 3`.

## Exercise 6: Separate a metric from the objective

The question is: Compare mean absolute residual and mean squared residual for [1, -1, 2].

The two measures have different units and emphasize large errors differently. Reporting one does not prove the other was optimized.

```python
np.testing.assert_allclose(residual.abs().mean().item(), 4 / 3, atol=1e-12, rtol=0)
assert residual.square().mean().item() == 2
```

**Expected:** MAE \(\frac{4}{3}\); MSE 2.

**Verify:** In a fresh process, the exercise checks confirm `residual.abs().mean().item()` matches `4 / 3` within 1e-12 and `residual.square().mean().item() == 2`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
