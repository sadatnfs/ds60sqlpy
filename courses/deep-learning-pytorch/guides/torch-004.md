# torch-004: Loss functions, reductions and gradient scale

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-003`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A loss is a numerical objective with a declared unit and denominator. The central investigation is concrete: Use residuals[1, -1, 2] against zero targets. The finish condition is squared entries1, 1, 4; sum6; mean2. MAE4/3; MSE2. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A loss is a numerical objective with a declared unit and denominator. Squared residuals have squared target units. Summing losses makes the objective scale with the number of participating entries; averaging removes that count from the scalar but changes gradient magnitude. PyTorch MSELoss with reduction='mean' averages all tensor elements, not an abstract notion of records inferred from their meaning. If each record has several outputs, those outputs also enter the denominator.

Compare reductions before comparing learning rates or frameworks. Duplicating a batch doubles a sum loss and its gradient but leaves a mean unchanged when every observation is duplicated equally. A metric such as absolute error may be reported beside squared loss, but it is not the same quantity. Masked objectives need a numerator and denominator using the same participation rule; zeroing excluded entries while dividing by padded length changes the objective.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-004](../../deep-learning-tensorflow/guides/tf-004.md) after deriving the shared numerical contract.

Compare PyTorch MSELoss reduction with the exact TensorFlow loss configuration, including any feature reduction performed before batch reduction. The paired scalar fixture agrees when shapes and denominators match. A framework default is not a substitute for naming the objective.

## Vocabulary and concepts

**Reduction:** The rule combining per-entry losses into a scalar.

**Loss unit:** The measurement unit implied by the objective.

**Gradient scale:** The magnitude change induced by objective scaling.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-004/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-004.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-004.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

F.mse_loss accepts prediction and target tensors; this course validates exact shape equality before calling it. reduction='none' preserves per-entry losses, 'sum' adds them, and'mean' divides by the number of elements. autograd.grad returns derivatives without accumulating into leaf.grad. Use a fresh forward graph for each independent derivative comparison.

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

**Expected:** squared entries1, 1, 4; sum6; mean2.

### Example B: Duplicate the batch

Duplicating observations does not create new information, but it changes a sum objective. This matters when comparing updates across batch sizes.

```python
duplicated=residual.repeat(2)
assert F.mse_loss(duplicated,torch.zeros_like(duplicated),reduction='sum').item()==12
assert F.mse_loss(duplicated,torch.zeros_like(duplicated),reduction='mean').item()==2
```

**Expected:** sum12; mean2.

### Example C: Compare derivative scale

The reduction scales every derivative by the same factor. A learning-rate comparison that ignores this can mistake an objective change for optimizer behavior.

```python
a=residual.clone().requires_grad_(); gsum=torch.autograd.grad((a*a).sum(),a)[0]
b=residual.clone().requires_grad_(); gmean=torch.autograd.grad((b*b).mean(),b)[0]
torch.testing.assert_close(gsum,3*gmean,atol=1e-12,rtol=0)
```

**Expected:** sum gradient equals3 times mean gradient.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: squared entries1, 1, 4; sum6; mean2. MAE4/3; MSE2. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compute residual reductions.** Use residuals[1, -1, 2] against zero targets.
   **Expected:** squared entries1, 1, 4; sum6; mean2.
   **Verify:** Save the assertion results for exercise 1, including squared entries1, 1, 4; sum6; mean2.

2. **Duplicate the batch.** Repeat every residual twice and compare reductions.
   **Expected:** sum12; mean2.
   **Verify:** Save the assertion results for exercise 2, including sum12; mean2.

3. **Compare derivative scale.** Differentiate sum and mean squared loss for a fresh3-entry tensor.
   **Expected:** sum gradient equals3 times mean gradient.
   **Verify:** Save the assertion results for exercise 3, including sum gradient equals3 times mean gradient.

4. **Inspect a feature denominator.** Use a2x2 residual matrix of ones and mean reduction.
   **Expected:** loss1 and4 participating elements.
   **Verify:** Save the assertion results for exercise 4, including loss1 and4 participating elements.

5. **Mask numerator and denominator together.** Use losses[1, 4, 100] with mask True, True, False.
   **Expected:** valid mean2.5, not5/3.
   **Verify:** Save the assertion results for exercise 5, including valid mean2.5, not5/3.

6. **Separate a metric from the objective.** Compare mean absolute residual and mean squared residual for[1, -1, 2].
   **Expected:** MAE4/3; MSE2.
   **Verify:** Save the assertion results for exercise 6, including MAE4/3; MSE2.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

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
