# torch-004: Loss functions, reductions and gradient scale

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-003`.

## Learning objectives

Choose a loss reduction deliberately and predict how sum, mean and masked means change the loss value and the gradient scale.

Central investigation: Reduce the residuals [1, -1, 2] with sum and mean, duplicate the batch, differentiate both objectives and mask a padded loss.

Finish condition: Sum is 6 and mean is 2, duplication doubles only the sum, the sum gradient is 3 times the mean gradient, and the masked mean of [1, 4, 100] with the last entry invalid is 2.5 rather than \(\frac{5}{3}\).

## Purpose and mental model

A loss is a numerical objective with a declared unit and denominator. Squared residuals have squared target units. Summing losses makes the objective scale with the number of participating entries; averaging removes that count from the scalar but changes gradient magnitude. PyTorch MSELoss with reduction='mean' averages all tensor elements, not an abstract notion of records inferred from their meaning. If each record has several outputs, those outputs also enter the denominator.

Compare reductions before comparing learning rates or frameworks. Duplicating a batch doubles a sum loss and its gradient but leaves a mean unchanged when every observation is duplicated equally. A metric such as absolute error may be reported beside squared loss, but it is not the same quantity. Masked objectives need a numerator and denominator using the same participation rule; zeroing excluded entries while dividing by padded length changes the objective.

## Design decisions and when to use this method

Choose the reduction and participation unit before comparing model scores or learning rates. Elementwise means are appropriate only when every included element should receive equal weight. An equal-example objective, equal-group objective and equal-token objective can differ when lengths or group sizes differ. Preserve the numerator and denominator as inspectable quantities.

Use squared error when its penalty matches the problem and its units are understood. Report another metric when it answers a useful evaluation question, but do not choose that metric after seeing which model it favors. A changed reduction changes the objective and gradient scale; it is not automatically evidence that the optimizer became more or less stable.

## Paired TensorFlow comparison

Compare [tf-004](../../deep-learning-tensorflow/guides/tf-004.md) after deriving the shared numerical contract.

Compare PyTorch MSELoss reduction with the exact TensorFlow loss configuration, including any feature reduction performed before batch reduction. The paired scalar fixture agrees when shapes and denominators match. A framework default is not a substitute for naming the objective.

## Vocabulary and concepts

**Reduction:** The rule combining per-entry losses into a scalar.

**Loss unit:** The measurement unit implied by the objective.

**Gradient scale:** The magnitude change induced by objective scaling.

## How to run this lesson

Run `torch-004` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `residual` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

F.mse_loss accepts prediction and target tensors; a paired-record application should validate exact shape equality before calling it; these literal fixtures construct matching shapes. reduction='none' preserves per-entry losses, 'sum' adds them, and'mean' divides by the number of elements. autograd.grad returns derivatives without accumulating into leaf.grad. Use a fresh forward graph for each independent derivative comparison.

## The denominator determines the gradient

For predictions and targets with identical shape (B, D), let \(r_{bd}=\mathrm{prediction}_{bd}-\mathrm{target}_{bd}\). The squared-error sum is \(S=\sum_b\sum_d r_{bd}^2\). PyTorch's mean MSE divides by B×D, so \(L=\frac{S}{BD}\). Its derivative with respect to each prediction is \(\frac{2r_{bd}}{BD}\). The sum objective instead gives 2 r_bd. This is why changing a reduction changes every gradient even when the forward residuals are identical. [PyTorch 2.9 MSELoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MSELoss.html).

For the residual vector [1, -1, 2], \(S=6\) and \(N=3\). The sum gradient is [2, -2, 4], while the mean gradient is [\(\frac{2}{3}\), \(\frac{-2}{3}\), \(\frac{4}{3}\)]. Duplicating every record doubles the sum and duplicates its derivative contributions. The mean objective remains two because both numerator and denominator double. This argument assumes equal replication of all participating entries; selectively repeating hard examples changes their weighting.

A two-output example makes the semantic unit visible. WithB=2, \(D=2\) and all residuals equal to one, the element mean is one, the total sum is four, and the mean of per-example feature sums is two. The first objective gives each scalar derivative 0.5; the last gives each scalar derivative 1. Both can be mathematically legitimate, but they encode different scaling. A framework cannot infer which one the application intended from the word mean.

Masking must use the same participation rule in the numerator and denominator. Keeping only the first two residuals gives numerator 2, count 2 and loss 1. Zeroing the third contribution and then averaging the original three positions gives \(\frac{2}{3}\). The valid mean gradient for the retained residuals is [1, -1]; dividing by the padded length shrinks it to [\(\frac{2}{3}\), \(\frac{-2}{3}\)]. Padding can therefore change both reported quality and training updates without adding any new observation.

An all-false mask is not the same as two accepted residuals equal to zero. The former has no defined mean denominator; the latter has a valid zero loss. Decide whether the surrounding pipeline should reject an empty objective or skip an update under an explicit policy. Silently calling it a perfect batch hides a missing-data condition.

Group weighting provides another counterexample. If one group contains residual [2] and another contains [0, 0, 0], the all-record MSE is \(\frac{4}{4}=1\). The unweighted mean of group MSEs is (4+0)/2=2. The correct choice depends on whether equal influence belongs to observations or groups. Accumulation and distributed-gradient chapters return to this denominator problem when batch sizes differ.

Finally, loss and evaluation metric need not rank candidates the same way. Residuals [0, 0, 4] have MAE \(\frac{4}{3}\) and MSE \(\frac{16}{3}\); residuals [2, 2, 2] have MAE 2 and MSE 4. Squared error prefers the second candidate because it penalizes the large miss more strongly, while absolute error prefers the first. State the objective and error costs before seeing the ranking.

## Worked example / walkthrough

### Example A: Compute residual reductions

The sum and mean differ only by the known count 3 here. Neither value can be interpreted without its denominator and squared-unit label.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

residual = torch.tensor([1.0, -1.0, 2.0], dtype=torch.float64)
zero = torch.zeros_like(residual)
assert F.mse_loss(residual, zero, reduction="sum").item() == 6
assert F.mse_loss(residual, zero, reduction="mean").item() == 2
torch.testing.assert_close(
    F.mse_loss(residual, zero, reduction="none"), torch.tensor([1.0, 1.0, 4.0], dtype=torch.float64)
)
```

**Expected:** squared entries 1, 1, 4; sum 6; mean 2.

### Example B: Duplicate the batch

Duplicating observations does not create new information, but it changes a sum objective. This matters when comparing updates across batch sizes.

```python
duplicated = residual.repeat(2)
assert F.mse_loss(duplicated, torch.zeros_like(duplicated), reduction="sum").item() == 12
assert F.mse_loss(duplicated, torch.zeros_like(duplicated), reduction="mean").item() == 2
```

**Expected:** sum 12; mean 2.

### Example C: Compare derivative scale

The reduction scales every derivative by the same factor. A learning-rate comparison that ignores this can mistake an objective change for optimizer behavior.

```python
a = residual.clone().requires_grad_()
gsum = torch.autograd.grad((a * a).sum(), a)[0]
b = residual.clone().requires_grad_()
gmean = torch.autograd.grad((b * b).mean(), b)[0]
torch.testing.assert_close(gsum, 3 * gmean, atol=1e-12, rtol=0)
```

**Expected:** sum gradient equals 3 times mean gradient.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Compute residual reductions. Predict exercise 6, Separate a metric from the objective, from its prompt alone: Compare mean absolute residual and mean squared residual for [1, -1, 2]. Then explain why this finish condition holds: Sum is 6 and mean is 2, duplication doubles only the sum, the sum gradient is 3 times the mean gradient, and the masked mean of [1, 4, 100] with the last entry invalid is 2.5 rather than \(\frac{5}{3}\). Keep each prediction beside the observed value.

## Exercises

1. **Reduce a new residual vector.** Use residuals [3, 0, -1, 2] against zero targets and compute the sum and mean squared reductions.
   **Expected:** squared entries 9, 0, 1, 4; sum 14; mean 3.5.
   **Verify:** In a fresh process, the exercise checks confirm `F.mse_loss(fresh, zeros, reduction='sum').item() == 14` and `F.mse_loss(fresh, zeros, reduction='mean').item() == 3.5`.

2. **Predict the effect of an appended zero.** Append one zero residual to the same vector and recompute both reductions before running them.
   **Expected:** sum stays 14; mean falls to 2.8 because the denominator becomes 5.
   **Verify:** In a fresh process, the exercise checks confirm `F.mse_loss(padded, torch.zeros_like(padded), reduction='sum').item() == 14` and `F.mse_loss(padded, torch.zeros_like(padded), reduction='mean').item()` matches `2.8` within 1e-12.

3. **Compare gradient scale for four entries.** Differentiate the sum and the mean of squares for a fresh copy of [3, 0, -1, 2].
   **Expected:** sum gradient [6, 0, -2, 4]; it equals 4 times the mean gradient.
   **Verify:** In a fresh process, the exercise checks confirm `total_grad` matches `torch.tensor([6.0, 0.0, -2.0, 4.0], dtype=torch.float64)` within 1e-12 and `total_grad` matches `4 * mean_grad` within 1e-12.

4. **Inspect a feature denominator.** Use a 2-by-2 residual matrix of ones and mean reduction.
   **Expected:** loss 1 and 4 participating elements.
   **Verify:** In a fresh process, the exercise checks confirm `F.mse_loss(matrix, torch.zeros_like(matrix)).item() == 1` and `matrix.numel() == 4`.

5. **Mask numerator and denominator together.** Use losses [1, 4, 100] with mask True, True, False.
   **Expected:** valid mean 2.5, not \(\frac{5}{3}\).
   **Verify:** In a fresh process, the exercise checks confirm `valid.item() == 2.5` and `valid.item() != 5 / 3`.

6. **Separate a metric from the objective.** Compare mean absolute residual and mean squared residual for [1, -1, 2].
   **Expected:** MAE \(\frac{4}{3}\); MSE 2.
   **Verify:** In a fresh process, the exercise checks confirm `residual.abs().mean().item()` matches `4 / 3` within 1e-12 and `residual.square().mean().item() == 2`.

## Common pitfalls and diagnosis

If duplicating a batch changes a reported mean, inspect the actual reduction and any mask or weight denominator. If adding padding makes the objective smaller, compare the included count with the tensor's total element count. If gradients differ by a constant factor across implementations, check batch and feature reductions before adjusting the learning rate.

If the forward scalar agrees but gradients do not, inspect per-entry losses and shapes. Broadcasting can create a different pairing that accidentally shares one scalar value. If a masked batch has no participants, handle that absence explicitly instead of widening a tolerance around NaN. During TensorFlow comparison, inspect both feature reduction and batch/sample weighting; matching a function's name does not establish that the same axes entered the denominator.

## Progressive hints

Hint 1: Example B (Duplicate the batch) alters one assumption of Example A (Compute residual reductions). Hint 2: exercise 4, Inspect a feature denominator, should end at loss 1 and 4 participating elements. Work backward from it. Hint 3: exercise 5, Mask numerator and denominator together, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Compare derivative scale, from its inputs alone. Predict whether exercise 3, Compare gradient scale for four entries, survives one changed input. Then explain Reduction, Loss unit, Gradient scale in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Compute residual reductions) cannot be rebuilt without help, revisit `torch-003` first. `torch-005` (Derivatives, requires_grad and finite-difference checks) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22 for the Reduction, Loss unit, Gradient scale behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Why can changing batch size change a gradient even with the same records?**

A sum objective scales with count, and minibatch updates also change the parameter state seen by later batches. Separate reduction effects from trajectory effects.

**Does mean always mean per-example mean?**

No. PyTorch MSELoss averages tensor elements. The semantic example unit must be mapped to axes explicitly.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-004, Loss functions, reductions and gradient scale.
Read courses/deep-learning-pytorch/guides/torch-004.md and courses/deep-learning-pytorch/lessons/torch-004.py. Direct prerequisites: `torch-003`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
