# torch-005: Derivatives, requires_grad and finite-difference checks

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-004`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A derivative measures local sensitivity:how much a function changes for a small input change. The central investigation is concrete: Differentiate (w-2)**2 at w=0 using autograd.grad. The finish condition is derivative -4; loss4. all raise ValueError. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A derivative measures local sensitivity:how much a function changes for a small input change. It is not itself a new parameter value. Gradient descent combines the derivative with a learning rate and a subtraction rule. PyTorch tracks operations involving tensors with requires_grad=True and can calculate a derivative through autograd.grad. A central finite difference estimates the same slope by evaluating the function at nearby inputs, providing an independent numerical check.

Finite differences involve a tradeoff:large steps measure a wider region, while extremely small steps lose precision through subtract iv e cancellation. Float64 is useful for this small diagnostic. At a nondifferentiable kink, a framework's chosen subgradient convention need not equal a symmetric finite difference. This lesson uses a smooth quadratic so the expected derivative is exact and the comparison is interpretable.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-005](../../deep-learning-tensorflow/guides/tf-005.md) after deriving the shared numerical contract.

TensorFlow GradientTape.gradient returns gradients explicitly, while PyTorch autograd.grad also returns them and backward accumulates into leaf.grad. Both must record the relevant forward computation. The same float64 finite-difference oracle applies to either framework.

## Vocabulary and concepts

**Derivative:** The local rate of change of a function.

**Finite difference:** A numerical slope estimate from nearby function evaluations.

**Learning rate:** A multiplier converting a gradient into an update magnitude.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-005/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-005.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-005.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Forf(w)=(w-2)^2, the analytic derivative is2(w-2). Construct a scalar float64 tensor with requires_grad=True, calculate f, and request autograd.grad(f, w). The returned tensor does not automatically populate w.grad. A central difference uses(f(w+h)-f(w-h))/(2 h). Validate positive finite h and finite function values before comparing.

## Worked example / walkthrough

### Example A: Derive a scalar slope

The analytic derivative provides an oracle independent of autograd. The negative sign means increasing w locally decreases the loss.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
def central(function,value,h):
    if not np.isfinite(h) or h<=0: raise ValueError('positive finite step required')
    left,right=function(value-h),function(value+h)
    if not np.isfinite([left,right]).all(): raise ValueError('finite probe values required')
    return (right-left)/(2*h)
w=torch.tensor(0.,dtype=torch.float64,requires_grad=True); loss=(w-2)**2
gradient=torch.autograd.grad(loss,w)[0]
assert gradient.item()==-4 and loss.item()==4
```

**Expected:** derivative -4; loss4.

### Example B: Check three finite differences

The quadratic central difference is especially clean. This does not imply every function or every step size achieves the same tolerance.

```python
for h in [.1,.01,.001]:
    slope=central(lambda value:(value-2)**2,0.,h)
    np.testing.assert_allclose(slope,-4,atol=1e-10,rtol=0)
```

**Expected:** all agree within1e-10.

### Example C: Separate gradient from update

The update includes direction, step size and old state. Treating the gradient as the parameter would implement a different algorithm.

```python
updated=0.-.1*gradient.item()
np.testing.assert_allclose(updated,.4,atol=1e-12,rtol=0)
assert updated!=gradient.item()
```

**Expected:** neww.4, not-4.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: derivative -4; loss4. all raise ValueError. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Derive a scalar slope.** Differentiate (w-2)**2 at w=0 using autograd.grad.
   **Expected:** derivative -4; loss4.
   **Verify:** Save the assertion results for exercise 1, including derivative -4; loss4.

2. **Check three finite differences.** Useh.1, .01, .001 atw0 and compare each slope with-4.
   **Expected:** all agree within1e-10.
   **Verify:** Save the assertion results for exercise 2, including all agree within1e-10.

3. **Separate gradient from update.** Use learning rate.1 and gradient-4 from w0.
   **Expected:** neww.4, not-4.
   **Verify:** Save the assertion results for exercise 3, including neww.4, not-4.

4. **Inspect a stationary point.** Differentiate the same objective atw2.
   **Expected:** gradient0 and loss0.
   **Verify:** Save the assertion results for exercise 4, including gradient0 and loss0.

5. **Observe grad-return behavior.** Check that autograd.grad did not accumulate into the leaf.grad field.
   **Expected:** w.grad is None despite a returned derivative.
   **Verify:** Save the assertion results for exercise 5, including w.grad is None despite a returned derivative.

6. **Reject invalid probes.** Pass h0, negative h and a function returning infinity to the finite-difference helper.
   **Expected:** all raise ValueError.
   **Verify:** Save the assertion results for exercise 6, including all raise ValueError.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Derivative, Finite difference, Learning rate using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-004` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why not make h arbitrarily tiny?**

Subtraction of nearly equal floating-point values loses significant digits. A smaller mathematical step can produce a worse numerical estimate.

**What does a zero derivative prove?**

Only local stationarity for that variable and objective at the evaluated point. It does not by itself prove a global optimum or good generalization.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-005, Derivatives, requires_grad and finite-difference checks.
Read courses/deep-learning-pytorch/guides/torch-005.md and courses/deep-learning-pytorch/lessons/torch-005.py. Direct prerequisites: `torch-004`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
