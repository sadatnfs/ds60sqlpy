# torch-023: Debugging custom loops, accumulation and clipping

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-022`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A custom training loop can fail by disconnecting the graph, forgetting an update, reusing old gradients or applying an incorrect reduction. The central investigation is concrete: Detach \({\left(w-2\right)}^{2}\) before backward and inspect tracking. The finish condition is detached loss requires_grad False; backward raises RuntimeError. nonnegative and below \(\frac{56}{675}\). A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A custom training loop can fail by disconnecting the graph, forgetting an update, reusing old gradients or applying an incorrect reduction. Debug the first small state transition before adding epochs and logging infrastructure. A gradient of None means no stored derivative was produced for that parameter; a zero tensor may be a valid derivative. Clearing with set_to_none preserves that diagnostic distinction.

Gradient clipping limits a norm after backward and before the optimizer step. It does not repair invalid labels, nonfinite forward values or a data leak. The clip function returns the pre-clipping norm, which is useful for diagnostics. Repeatedly clipping large gradients may indicate an underlying objective or scale problem rather than a complete fix. This lesson uses exact scalar updates and a3, 4gradient vector so all observations have independent oracles.

## Design decisions and when to use this method

Debug one update with a fixed fixture before adding epochs, accumulation or performance tooling. Name which parameter state produced each loss and gradient, and observe the actual optimizer-held parameter objects. A numerically correct detached loss is not a differentiable training objective.

Use accumulation to implement a declared additive objective under a memory budget, not to assume every set of microbatches is equivalent to one large batch. Choose the global denominator first. Clip the accumulated gradient at the intended update boundary, after unscaling if mixed precision is used, and keep a nonfinite result as a failed update rather than a valid clipped number.

## Paired TensorFlow comparison

Compare [tf-023](../../deep-learning-tensorflow/guides/tf-023.md) after deriving the shared numerical contract.

TensorFlow GradientTape can return None for a disconnected variable; PyTorch may have an untracked loss or None grad field depending on how the disconnection occurred. Both need explicit failure handling. PyTorch's clip_grad_norm_works on the accumulated parameter gradients, so its position in the loop matters.

## Vocabulary and concepts

**Disconnected loss:** A value with no gradient path to the intended parameters.

**Gradient clipping:** Bounding gradient magnitude before an update.

**Update trace:** A sequence of parameter, loss and gradient observations.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-023/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-023.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-023.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Check loss.requires_grad and parameter.grad before calling step. Use optimizer.zero_grad(set_to_none=True) for independent updates. nn.utils.clip_grad_norm_ mutates gradients in place and returns the norm before clipping. Record weight before, gradient before clipping, gradient after clipping and weight after step as distinct states. A detached numeric loss cannot backpropagate to its origin.

## Trace the optimizer state transition and objective denominator

Example A computes a numeric loss from \(w=0\) and detaches it. Its value is still four, but its dependency on w is no longer in the recorded graph. Setting requires_grad on that detached scalar would create a new leaf; it would not reconstruct the missing operation. The failed backward leaves the original parameter unchanged, so the sequential Example B still begins at \(w=0\).

For x=[1, 2, 3], y=2x and mean squared error, the objective is \(L(w)=\frac{14}{3}(w-2)^2\). Its derivative is \(\frac{28}{3}(w-2)\). With learning rate \(\frac{1}{10}\), the update is \(w_{\mathrm{next}}=\frac{w}{15}+\frac{28}{15}\). The exact trace is:

| Step | Weight before | Loss before | Gradient | Weight after |
| --- | --- | --- | --- | --- |
| first | 0 | \(\frac{56}{3}\) | \(\frac{-56}{3}\) | \(\frac{28}{15}\) |
| second | \(\frac{28}{15}\) | \(\frac{56}{675}\) | \(\frac{-56}{45}\) | \(\frac{448}{225}\) |

The loss at the final weight is \(\frac{56}{151875}\). A logged loss tensor calculated before step still represents the earlier state after the parameter changes. Recompute the forward objective to report post-update loss; printing the new weight beside the old loss without labeling them mixes two different states.

backward adds to stored gradient buffers. If the second step does not clear the first gradient, the stored value becomes \(\frac{-56}{3}-\frac{56}{45}=\frac{-896}{45}\), and the next weight becomes \(\frac{868}{225}\) rather than \(\frac{448}{225}\). That precise wrong trace distinguishes accidental accumulation from a wrong derivative formula. set_to_none=True also makes absence visible: None means no stored gradient was produced for that parameter in the relevant pass, whereas a connected derivative can be an actual zero. An optimizer may treat those cases differently, especially with state or decay.

Intentional microbatch accumulation needs a global denominator. Split the same three rows into one row and two rows at \(w=0\). The local mean gradients are -4 and -26. Averaging those means equally gives -15, but the full-data gradient is(1×(-4)+2×(-26))/3=\(\frac{-56}{3}\). One correct implementation weights each local mean by its valid-example count divided by the total, or accumulates local summed losses and divides by the total valid count. For padded tokens or sample weights, the denominator is the valid weight mass, not necessarily the number of stored rows.

This algebra assumes an additive loss evaluated at the same parameter state with equivalent forward behavior. Updating parameters between microbatches is a different trajectory. BatchNorm statistics, dropout draws, contrastive in-batch negatives and other batch-dependent computations can make a large batch differ even when gradient normalization is correct. State the scope of an equivalence claim rather than using accumulation as a universal replacement.

Norm clipping is another nonlinear boundary. Concatenate the participating parameter gradients into g. L2 clipping uses approximately g'=g×min(1, c/||g||), with a small numerical stabilizer in the implementation. For[3, 4], the norm is five and \(c=1\) gives approximately[0.6, 0.8]. The function returns the original five while mutating gradients in place. Starting from zero, plain SGD at 0.1 then moves to approximately[-0.06, -0.08]. [PyTorch 2.9 clip_grad_norm_](https://docs.pytorch.org/docs/2.9/generated/torch.nn.utils.clip_grad_norm_.html).

Clipping each contribution before accumulation can change the result. Scalar contributions 100 and-99 sum to one; clipping their sum to magnitude one leaves one. Clipping each separately to±1 and then adding gives zero. Therefore clip at the declared update boundary after the intended weighting and accumulation. With scaled gradients, unscale before applying a threshold expressed in ordinary gradient units.

Clipping limits the supplied gradient norm. It does not universally bound optimizer displacement when momentum, adaptive preconditioning, weight decay or retained state also affect the update. It also cannot repair invalid labels, nonfinite forward values or leakage. error_if_nonfinite=True makes an infinite/NaN norm a refusal rather than a meaningful update. The unchanged CPU fixture checks these local distinctions; it does not qualify mixed-precision or distributed execution.

## Worked example / walkthrough

### Example A: Expose detachment

The loss may have the correct numeric value while the training path is broken. Re-enabling requires_grad on the detached scalar would create a new leaf, not reconnect w.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); disconnected=((w-2)**2).detach()
assert not disconnected.requires_grad
try: disconnected.backward()
except RuntimeError: pass
else: raise AssertionError('detached loss backpropagated')
```

**Expected:** detached loss requires_grad False; backward raises RuntimeError.

### Example B: Repair two exact updates

Comparing each state finds the first divergence. A final-value-only check can hide wrong intermediate logging or compensating errors.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; optimizer=torch.optim.SGD([w],lr=.1); history=[]
for _ in range(2):
    optimizer.zero_grad(set_to_none=True); loss=((w*x-y)**2).mean(); loss.backward(); assert w.grad is not None; optimizer.step(); history.append(w.item())
np.testing.assert_allclose(history,[28/15,448/225],atol=1e-12,rtol=0)
```

**Expected:** weights \(\frac{28}{15}\) then \(\frac{448}{225}\).

### Example C: Inspect norm clipping

The function returns the original norm, not the new one. The small numerical difference comes from the stabilizing epsilon in the clip coefficient.

```python
parameter=nn.Parameter(torch.zeros(2)); parameter.grad=torch.tensor([3.,4.])
before=torch.nn.utils.clip_grad_norm_([parameter],1.)
assert before.item()==5; torch.testing.assert_close(parameter.grad,torch.tensor([.6,.8]),atol=1e-6,rtol=0)
```

**Expected:** returned norm 5; new gradient approximately.6, .8.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: detached loss requires_grad False; backward raises RuntimeError. nonnegative and below \(\frac{56}{675}\). Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Expose detachment.** Detach \({\left(w-2\right)}^{2}\) before backward and inspect tracking.
   **Expected:** detached loss requires_grad False; backward raises RuntimeError.
   **Verify:** Save the assertion results for exercise 1, including detached loss requires_grad False; backward raises RuntimeError.

2. **Repair two exact updates.** Use x 1, 2, 3, y = 2x, w = 0 and two SGD with rate 0.1 steps with gradient clearing.
   **Expected:** weights \(\frac{28}{15}\) then \(\frac{448}{225}\).
   **Verify:** Save the assertion results for exercise 2, including weights \(\frac{28}{15}\) then \(\frac{448}{225}\).

3. **Inspect norm clipping.** Assign gradient 3, 4 to a parameter vector and clip to norm 1.
   **Expected:** returned norm 5; new gradient approximately.6, .8.
   **Verify:** Save the assertion results for exercise 3, including returned norm 5; new gradient approximately.6, .8.

4. **Apply the clipped update.** Use SGD with rate 0.1 after clipping and inspect the parameter.
   **Expected:** approximately-.06, -.08.
   **Verify:** Save the assertion results for exercise 4, including approximately-.06, -.08.

5. **Reject nonfinite gradient norms.** Assign an infinite gradient and request error_if_nonfinite True.
   **Expected:** RuntimeError before a valid update.
   **Verify:** Save the assertion results for exercise 5, including RuntimeError before a valid update.

6. **Recompute post-update loss.** Calculate current loss after the two scalar updates and compare with the one-step oracle.
   **Expected:** nonnegative and below \(\frac{56}{675}\).
   **Verify:** Save the assertion results for exercise 6, including nonnegative and below \(\frac{56}{675}\).

## Common pitfalls and diagnosis

For an incorrect weight, compare the four columns of the exact trace and stop at the first mismatch. If the second gradient contains the first one, inspect zero_grad placement. If gradients are None, inspect the graph and optimizer parameter membership instead of replacing every missing value with zero. If loss is correct but untracked, look for detach, item, NumPy conversion or no_grad in the forward path.

If accumulation differs from a full-batch reference, compare valid counts and loss reductions before changing the learning rate. Then check batch-dependent forward behavior. If clipping returns five but the new gradient has norm near one, that is expected; the return is pre-clipping norm. If updates still look too large, inspect optimizer state and decay. A nonfinite gradient should stop the update and preserve diagnostic context, not be hidden by a permissive clipping call.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Disconnected loss, Gradient clipping, Update trace using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-022` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Is gradient clipping a fix for every exploding loss?**

No. It bounds one part of the update but does not repair wrong targets, unstable forward operations or bad reductions. Preserve and diagnose the first failure.

**Why record pre-clipping norms?**

The post-clipped normal one hides how often and how severely the gradient was altered. The original norm supports diagnosis and comparison.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-023, Debugging custom loops, accumulation and clipping.
Read courses/deep-learning-pytorch/guides/torch-023.md and courses/deep-learning-pytorch/lessons/torch-023.py. Direct prerequisites: `torch-022`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
