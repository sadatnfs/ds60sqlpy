# torch-004: Loss functions, reductions and gradient scale

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-003`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A loss is a numerical objective with a declared unit and denominator. The central investigation is concrete: Use residuals[1, -1, 2] against zero targets. The finish condition is squared entries 1, 1, 4; sum 6; mean 2. MAE 4/3; MSE 2. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-004/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-004.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-004.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

F.mse_loss accepts prediction and target tensors; a paired-record application should validate exact shape equality before calling it; these literal fixtures construct matching shapes. reduction='none' preserves per-entry losses, 'sum' adds them, and'mean' divides by the number of elements. autograd.grad returns derivatives without accumulating into leaf.grad. Use a fresh forward graph for each independent derivative comparison.

## The denominator determines the gradient

For predictions and targets with identical shape(B, D), let r_bd=prediction_bd-target_bd. The squared-error sum is S=Σ_bΣ_d r_bd². PyTorch's mean MSE divides byB×D, so L=S/(BD). Its derivative with respect to each prediction is 2 r_bd/(BD). The sum objective instead gives 2 r_bd. This is why changing a reduction changes every gradient even when the forward residuals are identical. [PyTorch 2.9 MSELoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MSELoss.html).

For the residual vector[1, -1, 2], S=6 and N=3. The sum gradient is[2, -2, 4], while the mean gradient is[2/3, -2/3, 4/3]. Duplicating every record doubles the sum and duplicates its derivative contributions. The mean objective remains two because both numerator and denominator double. This argument assumes equal replication of all participating entries; selectively repeating hard examples changes their weighting.

A two-output example makes the semantic unit visible. WithB=2, D=2 and all residuals equal to one, the element mean is one, the total sum is four, and the mean of per-example feature sums is two. The first objective gives each scalar derivative 0.5; the last gives each scalar derivative 1. Both can be mathematically legitimate, but they encode different scaling. A framework cannot infer which one the application intended from the word mean.

Masking must use the same participation rule in the numerator and denominator. Keeping only the first two residuals gives numerator 2, count 2 and loss 1. Zeroing the third contribution and then averaging the original three positions gives 2/3. The valid mean gradient for the retained residuals is[1, -1]; dividing by the padded length shrinks it to[2/3, -2/3]. Padding can therefore change both reported quality and training updates without adding any new observation.

An all-false mask is not the same as two accepted residuals equal to zero. The former has no defined mean denominator; the latter has a valid zero loss. Decide whether the surrounding pipeline should reject an empty objective orskip an update under an explicit policy. Silently calling it a perfect batch hides a missing-data condition.

Group weighting provides another counterexample. If one group contains residual[2] and another contains[0, 0, 0], the all-record MSE is 4/4=1. The unweighted mean of group MSEs is(4+0)/2=2. The correct choice depends on whether equal influence belongs to observations or groups. Accumulation and distributed-gradient chapters return to this denominator problem when batch sizes differ.

Finally, loss and evaluation metric need not rank candidates the same way. Residuals[0, 0, 4] have MAE 4/3 and MSE 16/3; residuals[2, 2, 2] have MAE 2 and MSE 4. Squared error prefers the second candidate because it penalizes the large miss more strongly, while absolute error prefers the first. State the objective and error costs before seeing the ranking.

## Worked example / walkthrough

### Example A: Compute residual reductions

The sum and mean differ only by the known count 3 here. Neither value can be interpreted without its denominator and squared-unit label.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

residual=torch.tensor([1.,-1.,2.],dtype=torch.float64); zero=torch.zeros_like(residual)
assert F.mse_loss(residual,zero,reduction='sum').item()==6
assert F.mse_loss(residual,zero,reduction='mean').item()==2
torch.testing.assert_close(F.mse_loss(residual,zero,reduction='none'),torch.tensor([1.,1.,4.],dtype=torch.float64))
```

**Expected:** squared entries 1, 1, 4; sum 6; mean 2.

### Example B: Duplicate the batch

Duplicating observations does not create new information, but it changes a sum objective. This matters when comparing updates across batch sizes.

```python
duplicated=residual.repeat(2)
assert F.mse_loss(duplicated,torch.zeros_like(duplicated),reduction='sum').item()==12
assert F.mse_loss(duplicated,torch.zeros_like(duplicated),reduction='mean').item()==2
```

**Expected:** sum 12; mean 2.

### Example C: Compare derivative scale

The reduction scales every derivative by the same factor. A learning-rate comparison that ignores this can mistake an objective change for optimizer behavior.

```python
a=residual.clone().requires_grad_(); gsum=torch.autograd.grad((a*a).sum(),a)[0]
b=residual.clone().requires_grad_(); gmean=torch.autograd.grad((b*b).mean(),b)[0]
torch.testing.assert_close(gsum,3*gmean,atol=1e-12,rtol=0)
```

**Expected:** sum gradient equals 3 times mean gradient.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: squared entries 1, 1, 4; sum 6; mean 2. MAE 4/3; MSE 2. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compute residual reductions.** Use residuals[1, -1, 2] against zero targets.
   **Expected:** squared entries 1, 1, 4; sum 6; mean 2.
   **Verify:** Save the assertion results for exercise 1, including squared entries 1, 1, 4; sum 6; mean 2.

2. **Duplicate the batch.** Repeat every residual twice and compare reductions.
   **Expected:** sum 12; mean 2.
   **Verify:** Save the assertion results for exercise 2, including sum 12; mean 2.

3. **Compare derivative scale.** Differentiate sum and mean squared loss for a fresh 3-entry tensor.
   **Expected:** sum gradient equals 3 times mean gradient.
   **Verify:** Save the assertion results for exercise 3, including sum gradient equals 3 times mean gradient.

4. **Inspect a feature denominator.** Use a2x2 residual matrix of ones and mean reduction.
   **Expected:** loss 1 and 4 participating elements.
   **Verify:** Save the assertion results for exercise 4, including loss 1 and 4 participating elements.

5. **Mask numerator and denominator together.** Use losses[1, 4, 100] with mask True, True, False.
   **Expected:** valid mean 2.5, not 5/3.
   **Verify:** Save the assertion results for exercise 5, including valid mean 2.5, not 5/3.

6. **Separate a metric from the objective.** Compare mean absolute residual and mean squared residual for[1, -1, 2].
   **Expected:** MAE 4/3; MSE 2.
   **Verify:** Save the assertion results for exercise 6, including MAE 4/3; MSE 2.

## Common pitfalls and diagnosis

If duplicating a batch changes a reported mean, inspect the actual reduction and any mask orweight denominator. If adding padding makes the objective smaller, compare the included count with the tensor's total element count. If gradients differ by a constant factor across implementations, check batch and feature reductions before adjusting the learning rate.

If the forward scalar agrees but gradients do not, inspect per-entry losses and shapes. Broadcasting can create a different pairing that accidentally shares one scalar value. If a masked batch has no participants, handle that absence explicitly instead of widening a tolerance aroundNaN. During TensorFlow comparison, inspect both feature reduction and batch/sample weighting; matching a function's name does not establish that the same axes entered the denominator.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Reduction, Loss unit, Gradient scale using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-003` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why can changing batch size change a gradient even with the same records?**

A sum objective scales with count, and minibatch updates also change the parameter state seen by later batches. Separate reduction effects from trajectory effects.

**Does mean always mean per-example mean?**

No. PyTorch MSELoss averages tensor elements. The semantic example unit must be mapped to axes explicitly.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-004, Loss functions, reductions and gradient scale.
Read courses/deep-learning-pytorch/guides/torch-004.md and courses/deep-learning-pytorch/lessons/torch-004.py. Direct prerequisites: `torch-003`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
