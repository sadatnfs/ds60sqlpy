# torch-005: Derivatives, requires_grad and finite-difference checks

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-004`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A derivative measures local sensitivity: how much a function changes for a small input change. The central investigation is concrete: Differentiate \({\left(w-2\right)}^{2}\) at \(w=0\) using autograd.grad. The finish condition is derivative -4; loss 4. all raise ValueError. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A derivative measures local sensitivity: how much a function changes for a small input change. It is not itself a new parameter value. Gradient descent combines the derivative with a learning rate and a subtraction rule. PyTorch tracks operations involving tensors with requires_grad=True and can calculate a derivative through autograd.grad. A central finite difference estimates the same slope by evaluating the function at nearby inputs, providing an independent numerical check.

Finite differences involve a tradeoff: large steps measure a wider region, while extremely small steps lose precision through subtractive cancellation. Float64 is useful for this small diagnostic. At a nondifferentiable kink, a framework's chosen subgradient convention need not equal a symmetric finite difference. This lesson uses a smooth quadratic so the expected derivative is exact and the comparison is interpretable.

## Design decisions and when to use this method

Use finite differences as a small independent diagnostic for a smooth scalar function or a selected coordinate of a larger computation. Recompute the complete forward function at each probe and keep parameters, data, model mode and randomness fixed. A stochastic dropout sample or changed minibatch can overwhelm the small difference being measured.

Prefer an analytic derivative when a tiny expression permits one, and compare several sensible probe sizes instead of declaring the smallest h best. Avoid interpreting a symmetric probe at a known kink as proof of an ordinary derivative. The helper is a bounded numerical check, not a certificate for every floating-point scale or a replacement for understanding the function's domain.

## Paired TensorFlow comparison

Compare [tf-005](../../deep-learning-tensorflow/guides/tf-005.md) after deriving the shared numerical contract.

TensorFlow GradientTape.gradient returns gradients explicitly, while PyTorch autograd.grad also returns them and backward accumulates into leaf.grad. Both must record the relevant forward computation. The same float64 finite-difference oracle applies to either framework.

## Vocabulary and concepts

**Derivative:** The local rate of change of a function.

**Finite difference:** A numerical slope estimate from nearby function evaluations.

**Learning rate:** A multiplier converting a gradient into an update magnitude.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-005`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-005.py` under `.learning/expansion/torch-005/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

For \(f(w)=(w-2)^2\), the analytic derivative is \(2(w-2)\). Construct a scalar float64 tensor with requires_grad=True, calculate f, and request autograd.grad(f, w). The returned tensor does not automatically populate w.grad. A central difference uses \(\frac{f(w+h)-f(w-h)}{2h}\). Validate positive finite h and finite function values before comparing.

## Derive the slope before using it as an update

For f(w)=(w-2)², expand the derivative or apply the square rule to obtain f'(w)=\(2(w-2)\). At \(w=0\) the loss is four and the derivative is -4. These are different quantities with different units: the derivative measures loss change per unit of w. A learning rate converts that sensitivity into a chosen parameter displacement. With rate 0.1, the update is 0-0.1(-4)=0.4 and the recomputed loss is(0.4-2)²=2.56.

The central finite difference uses two probes separated by 2 h:

`D_h = [f(w+h)-f(w-h)]/(2h)`.

Expanding this particular quadratic gives f(w+h)-f(w-h)=4h(w-2), so D_h=\(2(w-2)\) exactly in real arithmetic. This special cancellation explains why the three supplied h values agree unusually well. It does not establish that central differences are exact for arbitrary nonlinear functions. For a sufficiently smooth general function, the leading truncation error is proportional to h² and a third derivative near the probe point.

A forward difference has a different error even on this quadratic. At zero, [f(h)-f(0)]/h=-4+h. Thus \(h=0.1\) gives -3.9, \(h=0.01\) gives -3.99, and \(h=0.001\) gives -3.999. The visible offset is a property of the numerical approximation, not an autograd error. Deriving the approximation's expected bias prevents a correct implementation from being rejected for the wrong reason.

Floating-point cancellation pushes in the opposite direction from truncation error. As h shrinks, the two function values can become nearly equal compared with their magnitude. Their subtraction can lose meaningful digits, and a sufficiently small perturbation may not change the represented point at all. Scaling, dtype and the function's local behavior all matter. Sweep several probe scales and inspect the error curve rather than applying a universal h or tolerance.

The probe distance h is not the optimizer learning rate. A probe estimates local sensitivity without choosing a training trajectory; an update deliberately changes model state. A negative derivative identifies a locally descending direction, but a large finite update can still overshoot. For the supplied quadratic, a rate 1.1 update from zero moves to 4.4 and increases loss to 5.76, despite using the correct derivative.

At abs(w) around zero, the left slope is -1 and the right slope is+1. A symmetric probe returns zero because the sides cancel, even though no unique ordinary derivative exists. ReLU gives a related counterexample: its symmetric slope at zero is 0.5 while PyTorch's selected backward convention is zero. Use a smooth point when checking equality with a classical derivative; at a kink, explain the convention separately.

Finally, `autograd.grad` returns the requested derivatives. It does not mean that the leaf's `.grad` buffer was populated. The return tuple and the accumulation behavior of `backward` are separate interfaces. [PyTorch 2.9 autograd.grad](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad.html). A returned -4 with w.grad stillNone is therefore expected here, while a genuinely disconnected path requires a different diagnosis.

## Worked example / walkthrough

### Example A: Derive a scalar slope

The analytic derivative provides an oracle independent of autograd. The negative sign means increasing w locally decreases the loss.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
def central(function,value,h):
    if not np.isfinite(value): raise ValueError('finite probe point required')
    if not np.isfinite(h) or h<=0: raise ValueError('positive finite step required')
    left,right=function(value-h),function(value+h)
    if not np.isfinite([left,right]).all(): raise ValueError('finite probe values required')
    return (right-left)/(2*h)
w=torch.tensor(0.,dtype=torch.float64,requires_grad=True); loss=(w-2)**2
gradient=torch.autograd.grad(loss,w)[0]
assert gradient.item()==-4 and loss.item()==4
```

**Expected:** derivative -4; loss 4.

### Example B: Check three finite differences

The quadratic central difference is especially clean. This does not imply every function or every step size achieves the same tolerance.

```python
for h in [.1,.01,.001]:
    slope=central(lambda value:(value-2)**2,0.,h)
    np.testing.assert_allclose(slope,-4,atol=1e-10,rtol=0)
```

**Expected:** all agree within 1e-10.

### Example C: Separate gradient from update

The update includes direction, step size and old state. Treating the gradient as the parameter would implement a different algorithm.

```python
updated=0.-.1*gradient.item()
np.testing.assert_allclose(updated,.4,atol=1e-12,rtol=0)
assert updated!=gradient.item()
```

**Expected:** new \(w=0.4\), not-4.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: derivative -4; loss 4. all raise ValueError. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Derive a scalar slope.** Differentiate \({\left(w-2\right)}^{2}\) at \(w=0\) using autograd.grad.
   **Expected:** derivative -4; loss 4.
   **Verify:** Save the assertion results for exercise 1, including derivative -4; loss 4.

2. **Check three finite differences.** Use \(h=0.1\), .01, .001 at \(w=0\) and compare each slope with-4.
   **Expected:** all agree within 1e-10.
   **Verify:** Save the assertion results for exercise 2, including all agree within 1e-10.

3. **Separate gradient from update.** Use learning rate 0.1 and gradient-4 from w = 0.
   **Expected:** new \(w=0.4\), not-4.
   **Verify:** Save the assertion results for exercise 3, including new \(w=0.4\), not-4.

4. **Inspect a stationary point.** Differentiate the same objective atw 2.
   **Expected:** gradient 0 and loss 0.
   **Verify:** Save the assertion results for exercise 4, including gradient 0 and loss 0.

5. **Observe grad-return behavior.** Check that autograd.grad did not accumulate into the leaf.grad field.
   **Expected:** w.grad is None despite a returned derivative.
   **Verify:** Save the assertion results for exercise 5, including w.grad is None despite a returned derivative.

6. **Reject invalid probes.** Pass \(h=0\), negative h and a function returning infinity to the finite-difference helper.
   **Expected:** all raise ValueError.
   **Verify:** Save the assertion results for exercise 6, including all raise ValueError.

## Common pitfalls and diagnosis

If the numerical slope changes erratically as h shrinks, inspect whether w+h and w-h remain distinct represented numbers and whether the function values are finite. If the result is a stable factor-of-two error, check the 2 h denominator. If the probe reports zero unexpectedly, verify that the callable recomputes the complete function rather than closing over a previously calculated activation.

Reject a nonfinite probe point explicitly, even when a constant callable would return finite outputs and hide that invalid point. Keep a missing gradient path separate from a connected derivative of zero. If a correct negative derivative produces a higher updated loss, recompute the new objective and inspect the learning rate before altering the derivative. At a kink, record one-sided behavior and the framework convention instead of widening a tolerance until incompatible mathematical objects appear equal.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Derivative, Finite difference, Learning rate using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-004` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why not make h arbitrarily tiny?**

Subtraction of nearly equal floating-point values loses significant digits. A smaller mathematical step can produce a worse numerical estimate.

**What does a zero derivative prove?**

Only local stationarity for that variable and objective at the evaluated point. It does not by itself prove a global optimum or good generalization.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-005, Derivatives, requires_grad and finite-difference checks.
Read courses/deep-learning-pytorch/guides/torch-005.md and courses/deep-learning-pytorch/lessons/torch-005.py. Direct prerequisites: `torch-004`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
