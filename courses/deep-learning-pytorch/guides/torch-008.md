# torch-008: One optimizer step you can audit

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-007`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

One optimizer step is the smallest complete training experiment. The central investigation is concrete: Use float64 x = [1, 2, 3], y = 2x and scalar w = 0. The finish condition is mean squared loss \(\frac{56}{3}\). w.grad None; updated weight unchanged. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

One optimizer step is the smallest complete training experiment. Specify inputs, targets, initial weight, dtype, loss reduction, learning rate and optimizer rule. Calculate the forward loss, derive the gradient, apply the update and recompute the loss at the new state. A PyTorch optimizer does not calculate gradients itself: backward populates the parameter.grad fields and optimizer.step consumes them. zero_grad establishes which contributions belong to the next step.

The scalar fixture x = [1, 2, 3], y = 2x, w = 0 and rate 0.1 has an exact oracle. Mean squared loss starts at \(\frac{56}{3}\), the derivative is-\(\frac{56}{3}\), the new weight is \(\frac{28}{15}\), and the new loss is \(\frac{56}{675}\). A mistakenly broadcast column target gives the same initial loss but a different gradient. This is why comparing only a printed initial objective is an inadequate correctness test.

## Design decisions and when to use this method

Use this one-step audit before trusting a longer training loop, porting an optimizer path or comparing frameworks. Fix every input, initial value and reduction so a disagreement can be localized to forward computation, backward accumulation or parameter mutation. Start with plain SGD, zero momentum and zero weight decay before adding stateful optimizer behavior.

A successful update is evidence about this numerical mechanism. It is not a model-quality result, and the exact learning-rate interval derived here belongs only to this one-parameter quadratic. Later nonlinear, stochastic and distributed models require their own scale and stability analysis rather than borrowing this bound as a default.

## Paired TensorFlow comparison

Compare [tf-008](../../deep-learning-tensorflow/guides/tf-008.md) after deriving the shared numerical contract.

The paired TensorFlow GradientTape example has the same arithmetic oracle. PyTorch separates backward accumulation and optimizer.step, while the TensorFlow example explicitly passes returned gradients to an update. Both need an exact shape contract and a fresh post-update forward calculation.

## Vocabulary and concepts

**Optimizer membership:** The exact parameter objects whose gradients an optimizer consumes.

**SGD step:** Subtracting learning rate times the current gradient.

**Independent oracle:** A separately derived expected result for the computation.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-008`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-008.py` under `.learning/expansion/torch-008/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Wrap the scalar weight in nn.Parameter with float64. Use an SGD optimizer with momentum 0 and no weight decay. Call zero_grad, set the mean squared residual objective, backward, save the gradient, then step. Use a fresh forward expression for the post-update loss. Validate prediction/target shape equality before allowing a production loss helper to rely on broadcasting.

## Derive the complete scalar training transition

The hypothesis is prediction_i=w x_i for x=[1, 2, 3] and y=2x. With a mean over three paired observations, the objective simplifies to:

`L(w) = (1²+2²+3²)(w-2)²/3 = (14/3)(w-2)²`.

Its derivative is`g(w)=(28/3)(w-2)`. At \(w=0\), the predictions are zeros, residuals[-2, -4, -6], squared errors[4, 16, 36], loss \(\frac{56}{3}\) and gradient-\(\frac{56}{3}\). The input features can remain ordinary constant tensors because the requested derivative is with respect to w. Targets also remain fixed labels rather than state the optimizer is allowed to change.

For learning rateη=1/10, plain SGD gives w_new=w-ηg=28/15. The new residual is(w_new-2)x=(-2/15)x, so its entries are[-2/15, \(\frac{-4}{15}\), -6/15]. Squaring and averaging gives \(\frac{56}{675}\). The before-loss, gradient, new parameter and after-loss are four separately inspected observations:

| Stage | Weight | Quantity observed |
| --- | --- | --- |
| Forward | 0 | \(L=\frac{56}{3}\) |
| Backward | 0 | stored \(\mathrm{gradient}=\frac{-56}{3}\) |
| Step | \(\frac{28}{15}\) | parameter changed by \(\frac{28}{15}\) |
| New forward | \(\frac{28}{15}\) | \(L=\frac{56}{675}\) |

Backward does not perform the update, and step does not recompute the loss. The old loss tensor still records the earlier forward result after the parameter changes. The fresh Parameter starts with no stored gradient, which makes the first backward unambiguous; repeated independent steps need an explicit clearing policy. The SGD API specifies how momentum, weight decay and other options would change this simpler transition. [PyTorch 2.9 SGD](https://docs.pytorch.org/docs/2.9/generated/torch.optim.SGD.html).

The exact quadratic also permits a stability calculation. Let \(e=w-2\) be the error from the optimum. One update gives e_new=(1-28η/3)e. Repeated full-batch updates contract this error only when|1-28η/3|<1, or 0<η<3/14. Atη=0.1, the contraction factor is \(\frac{1}{15}\). Atη=0.25, it is-4/3: the parameter crosses the optimum and its error grows. The first weight becomes \(\frac{14}{3}\) and the new loss \(\frac{896}{27}\), larger than the initial \(\frac{56}{3}\) despite a correct derivative.

Changing to a summed objective changes that bound because the gradient is three times larger. This is why learning-rate claims require a declared denominator. The result is exact for this fixed convex scalar objective; it is not a universal neural-network learning-rate rule.

The mistaken column target produces a different objective over every input-target pair. Its mean can be expanded as`L_bad(w)=(14/3)w²-16w+56/3`. At zero, it shares the correct initial loss \(\frac{56}{3}\), but its derivative is-16. Its optimum is \(\frac{12}{7}\) rather than two, and its minimum is \(\frac{104}{21}\) rather than zero. This is a changed statistical pairing, not merely an objective-scale factor. Adjusting the learning rate to disguise the first gradient difference cannot restore the intended optimum.

An audit should therefore check the residual shape and per-record identity before reducing to a scalar. It should then compare the derivative with the independent NumPy probe and verify that the optimizer owns the exact Parameter object whose gradient was computed. Only after those boundaries pass does a longer loop add useful evidence.

## Worked example / walkthrough

### Example A: Calculate the initial loss

The three squared residuals are 4, 16, 36. Their sum 56 divided by three defines the objective denominator.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
loss=((w*x-y)**2).mean(); np.testing.assert_allclose(loss.item(),56/3,atol=1e-12,rtol=0)
```

**Expected:** mean squared loss \(\frac{56}{3}\).

### Example B: Inspect the gradient before updating

Backward computes derivatives but does not update the parameter. Separating these observations helps diagnose a missing optimizer step.

```python
loss.backward(); np.testing.assert_allclose(w.grad.item(),-56/3,atol=1e-12,rtol=0)
assert w.item()==0
```

**Expected:** gradient-\(\frac{56}{3}\); weight still 0.

### Example C: Apply exactly one SGD update

The optimizer consumes the stored gradient. The old loss tensor remains the before-update result, so the new loss requires another forward calculation.

```python
optimizer=torch.optim.SGD([w],lr=.1); optimizer.step()
np.testing.assert_allclose(w.item(),28/15,atol=1e-12,rtol=0)
np.testing.assert_allclose(((w*x-y)**2).mean().item(),56/675,atol=1e-12,rtol=0)
```

**Expected:** w28/15; loss \(\frac{56}{675}\).

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: mean squared loss \(\frac{56}{3}\). w.grad None; updated weight unchanged. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate the initial loss.** Use float64 x = [1, 2, 3], y = 2x and scalar w = 0.
   **Expected:** mean squared loss \(\frac{56}{3}\).
   **Verify:** Save the assertion results for exercise 1, including mean squared loss \(\frac{56}{3}\).

2. **Inspect the gradient before updating.** Back propagate the initial loss and compare with-\(\frac{56}{3}\).
   **Expected:** gradient-\(\frac{56}{3}\); weight still 0.
   **Verify:** Save the assertion results for exercise 2, including gradient-\(\frac{56}{3}\); weight still 0.

3. **Apply exactly one SGD update.** Use SGD learning rate 0.1 onw and recompute the objective afterward.
   **Expected:** w28/15; loss \(\frac{56}{675}\).
   **Verify:** Save the assertion results for exercise 3, including w28/15; loss \(\frac{56}{675}\).

4. **Expose the broadcast counterexample.** At a fresh w = 0, compare vector predictions with column targets shaped(3, 1).
   **Expected:** initial loss still \(\frac{56}{3}\), but gradient-16.
   **Verify:** Save the assertion results for exercise 4, including initial loss still \(\frac{56}{3}\), but gradient-16.

5. **Check a finite-difference gradient.** Use a plain NumPy scalar objective around w = 0 with h.001.
   **Expected:** slope-\(\frac{56}{3}\) within 1e-9.
   **Verify:** Save the assertion results for exercise 5, including slope-\(\frac{56}{3}\) within 1e-9.

6. **Clear the consumed gradient.** Call optimizer.zero_grad(set_to_none=True) after the step and inspect state.
   **Expected:** w.grad None; updated weight unchanged.
   **Verify:** Save the assertion results for exercise 6, including w.grad None; updated weight unchanged.

## Common pitfalls and diagnosis

If backward produces the right derivative but w remains zero, check whether step ran and whether the optimizer contains that exact Parameter object. If w changes but the reported loss stays \(\frac{56}{3}\), inspect whether code reused the old loss tensor instead of recomputing the forward expression. Clearing gradients should leave the updated parameter unchanged.

If the initial loss agrees but the gradient is-16, inspect for the(3, 3) broadcast grid before changing SGD. If a correct gradient increases the loss, check update sign and learning rate; the exact quadratic bound distinguishes overshoot from a differentiation defect. If a second update is identical to the first, check for a stale stored gradient. Preserve the four-stage trace so a failure can be attributed to the correct boundary rather than hidden inside one final scalar.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Optimizer membership, SGD step, Independent oracle using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-007` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why can the wrong broadcast have the same first loss?**

At \(w=0\) every prediction is zero, so repeating each target across a new axis leaves its mean squared magnitude unchanged. The derivative also depends on how each input is paired with targets, and that pairing changed.

**Does optimizer.step recompute the loss?**

No. It uses current gradients stored on its parameter objects. Forward calculation, backward and step are separate stages.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-008, One optimizer step you can audit.
Read courses/deep-learning-pytorch/guides/torch-008.md and courses/deep-learning-pytorch/lessons/torch-008.py. Direct prerequisites: `torch-007`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
