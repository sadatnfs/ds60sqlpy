# torch-006: Autograd graphs, the chain rule and in-place hazards

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-005`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Autograd follows the chain of tensor operations from a scalar objective back to its inputs. The central investigation is concrete: Use w=1, z=2*w, a=z*z and loss=(a-1)**2. The finish condition is z2, a4, loss9, gradient48. at new w=1.5, gradient -1 for (w-2)**2. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Autograd follows the chain of tensor operations from a scalar objective back to its inputs. Forz=2 w, a=z², loss=(a-1)², the derivative multiplies the local sensitivities along that chain. PyTorch builds the graph dynamically during the forward pass and saves values needed for backward. An in-place mutation can invalidate those saved values, so the framework uses version checks and restricts some mutations. A failure is a signal to understand ownership and graph lifetime, not a reason to bypass checks with.data.

Graph state is also temporary. After a normal backward pass, the saved intermediates are released; reusing the same graph for another backward usually requires an explicit retention policy or a fresh forward computation. Most training loops should recompute the forward graph per batch. Nonlinearities such as ReLU introduce points where a derivative convention matters.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-006](../../deep-learning-tensorflow/guides/tf-006.md) after deriving the shared numerical contract.

TensorFlow records a chosen tape scope, while PyTorch dynamically tracks operations involving requires_grad values. Both need the forward dependencies. PyTorch shared storage and in-place operations make saved-tensor versioning an especially visible debugging concern; avoid translating every TensorFlow assignment into an arbitrary PyTorch in-place edit.

## Vocabulary and concepts

**Autograd graph:** The recorded tensor-operation dependencies used for differentiation.

**Saved tensor:** An intermediate value retained because backward needs it.

**In-place hazard:** A mutation that changes data required by a recorded derivative.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-006/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-006.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-006.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Build every intermediate from a requires_grad leaf. autograd.grad(loss, w) composes the chain rule. A direct in-place add on a leaf requiring gradients raises RuntimeError unless performed under a deliberate no_grad update context. Mutating a saved input under no_grad can still make a later backward fail its version check. Use clone when a separate mutable value is needed and recompute the graph after optimizer updates.

## Worked example / walkthrough

### Example A: Trace the chain rule

The factors are2(loss inner), 2 z and2 from the affine input, with the outer residual included. Multiplying them gives48 at the supplied point.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w=torch.tensor(1.,dtype=torch.float64,requires_grad=True); z=2*w; a=z*z; loss=(a-1)**2
gradient=torch.autograd.grad(loss,w)[0]
assert (z.item(),a.item(),loss.item(),gradient.item())==(2.,4.,9.,48.)
```

**Expected:** z2, a4, loss9, gradient48.

### Example B: Check an independent slope

The finite difference treats the entire function as a black box. It can expose an incorrect manual chain factor without reading the graph internal s.

```python
h=1e-5; f=lambda value:((2*value)**2-1)**2
numeric=(f(1+h)-f(1-h))/(2*h)
np.testing.assert_allclose(numeric,48,atol=1e-5,rtol=0)
```

**Expected:** approximately48 within1e-5.

### Example C: Observe a leaf mutation guard

The guard prevents an ambiguous modification of a value whose derivative history is being tracked. Optimizer updates use a deliberate state-update boundary instead.

```python
leaf=torch.tensor(1.,requires_grad=True)
try: leaf.add_(1)
except RuntimeError: pass
else: raise AssertionError('unsafe leaf mutation accepted')
```

**Expected:** RuntimeError.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: z2, a4, loss9, gradient48. at new w=1.5, gradient -1 for (w-2)**2. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Trace the chain rule.** Use w=1, z=2*w, a=z*z and loss=(a-1)**2.
   **Expected:** z2, a4, loss9, gradient48.
   **Verify:** Save the assertion results for exercise 1, including z2, a4, loss9, gradient48.

2. **Check an independent slope.** Compare the chain derivative with a central difference of the complete scalar expression.
   **Expected:** approximately48 within1e-5.
   **Verify:** Save the assertion results for exercise 2, including approximately48 within1e-5.

3. **Observe a leaf mutation guard.** Try an in-place add on a leaf requiring gradients outside no_grad.
   **Expected:** RuntimeError.
   **Verify:** Save the assertion results for exercise 3, including RuntimeError.

4. **Expose saved-value invalidation.** Build loss=x*x, mutate x under no_grad before backward, and inspect the failure.
   **Expected:** RuntimeError from a changed saved tensor version.
   **Verify:** Save the assertion results for exercise 4, including RuntimeError from a changed saved tensor version.

5. **Inspect a ReLU convention.** Differentiate ReLU at negative, zero and positive inputs.
   **Expected:** gradients0, 0, 1.
   **Verify:** Save the assertion results for exercise 5, including gradients0, 0, 1.

6. **Recompute after an update.** Update a scalar under no_grad, then build a fresh quadratic objective and request its derivative.
   **Expected:** at new w=1.5, gradient -1 for (w-2)**2.
   **Verify:** Save the assertion results for exercise 6, including at new w=1.5, gradient -1 for (w-2)**2.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Autograd graph, Saved tensor, In-place hazard using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-005` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does no_grad make any mutation safe?**

No. It stops recording new operations, but a mutation can still invalidate values saved by an earlier graph. Update only at a deliberate boundary and recompute the forward pass.

**Why avoid.data as a work around?**

It can bypass useful autograd safeguards and create silently incorrect derivatives. Understand the graph and use documented no_grad, detach and clone semantics instead.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-006, Autograd graphs, the chain rule and in-place hazards.
Read courses/deep-learning-pytorch/guides/torch-006.md and courses/deep-learning-pytorch/lessons/torch-006.py. Direct prerequisites: `torch-005`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
