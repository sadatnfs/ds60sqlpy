# torch-008: One optimizer step you can audit

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-007`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

One optimizer step is the smallest complete training experiment. The central investigation is concrete: Use float64 x1, 2, 3, y2 x and scalar w0. The finish condition is mean squared loss56/3. w.grad None; updated weight unchanged. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

One optimizer step is the smallest complete training experiment. Specify inputs, targets, initial weight, dtype, loss reduction, learning rate and optimizer rule. Calculate the forward loss, derive the gradient, apply the update and recompute the loss at the new state. A PyTorch optimizer does not calculate gradients itself:backward populates the parameter.grad fields and optimizer.step consumes them. zero_grad establishes which contributions belong to the next step.

The scalar fixture x1, 2, 3, y2 x, w0 and rate.1 has an exact oracle. Mean squared loss starts at56/3, the derivative is-56/3, the new weight is28/15, and the new loss is56/675. A mistaken l y broadcast column target gives the same initial loss but a different gradient. This is why comparing only a printed initial objective is an inadequate correctness test.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-008](../../deep-learning-tensorflow/guides/tf-008.md) after deriving the shared numerical contract.

The paired TensorFlow GradientTape example has the same arithmetic oracle. PyTorch separates backward accumulation and optimizer.step, while the TensorFlow example explicitly passes returned gradients to an update. Both need an exact shape contract and a fresh post-update forward calculation.

## Vocabulary and concepts

**Optimizer membership:** The exact parameter objects whose gradients an optimizer consumes.

**SGD step:** Subtracting learning rate times the current gradient.

**Independent oracle:** A separately derived expected result for the computation.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-008/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-008.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-008.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Wrap the scalar weight innn.Parameter with float64. Use an SGD optimizer with momentum0 and no weight decay. Call zero_grad, set the mean squared residual objective, backward, save the gradient, then step. Use a fresh forward expression for the post-update loss. Validate prediction/target shape equality before allowing a production loss helper to rely on broadcasting.

## Worked example / walkthrough

### Example A: Calculate the initial loss

The three squared residuals are4, 16, 36. Their sum56 divided by three defines the objective denominator.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
loss=((w*x-y)**2).mean(); np.testing.assert_allclose(loss.item(),56/3,atol=1e-12,rtol=0)
```

**Expected:** mean squared loss56/3.

### Example B: Inspect the gradient before updating

Backward computes derivatives but does not update the parameter. Separating these observations helps diagnose a missing optimizer step.

```python
loss.backward(); np.testing.assert_allclose(w.grad.item(),-56/3,atol=1e-12,rtol=0)
assert w.item()==0
```

**Expected:** gradient-56/3; weight still0.

### Example C: Apply exactly one SGD update

The optimizer consumes the stored gradient. The old loss tensor remains the before-update result, so the new loss requires another forward calculation.

```python
optimizer=torch.optim.SGD([w],lr=.1); optimizer.step()
np.testing.assert_allclose(w.item(),28/15,atol=1e-12,rtol=0)
np.testing.assert_allclose(((w*x-y)**2).mean().item(),56/675,atol=1e-12,rtol=0)
```

**Expected:** w28/15; loss56/675.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: mean squared loss56/3. w.grad None; updated weight unchanged. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate the initial loss.** Use float64 x1, 2, 3, y2 x and scalar w0.
   **Expected:** mean squared loss56/3.
   **Verify:** Save the assertion results for exercise 1, including mean squared loss56/3.

2. **Inspect the gradient before updating.** Back propagate the initial loss and compare with-56/3.
   **Expected:** gradient-56/3; weight still0.
   **Verify:** Save the assertion results for exercise 2, including gradient-56/3; weight still0.

3. **Apply exactly one SGD update.** Use SGD learning rate.1 onw and recompute the objective afterward.
   **Expected:** w28/15; loss56/675.
   **Verify:** Save the assertion results for exercise 3, including w28/15; loss56/675.

4. **Expose the broadcast counterexample.** At a fresh w0, compare vector predictions with column targets shaped(3, 1).
   **Expected:** initial loss still56/3, but gradient-16.
   **Verify:** Save the assertion results for exercise 4, including initial loss still56/3, but gradient-16.

5. **Check a finite-difference gradient.** Use a plain NumPy scalar objective around w0 with h.001.
   **Expected:** slope-56/3 within1e-9.
   **Verify:** Save the assertion results for exercise 5, including slope-56/3 within1e-9.

6. **Clear the consumed gradient.** Call optimizer.zero_grad(set_to_none=True) after the step and inspect state.
   **Expected:** w.grad None; updated weight unchanged.
   **Verify:** Save the assertion results for exercise 6, including w.grad None; updated weight unchanged.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Optimizer membership, SGD step, Independent oracle using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-007` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why can the wrong broadcast have the same first loss?**

Atw0 every prediction is zero, so repeating each target across a new axis leaves its mean squared magnitude unchanged. The derivative also depends on how each input is paired with targets, and that pairing changed.

**Does optimizer.step recompute the loss?**

No. It uses current gradients stored on its parameter objects. Forward calculation, backward and step are separate stages.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-008, One optimizer step you can audit.
Read courses/deep-learning-pytorch/guides/torch-008.md and courses/deep-learning-pytorch/lessons/torch-008.py. Direct prerequisites: `torch-007`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
