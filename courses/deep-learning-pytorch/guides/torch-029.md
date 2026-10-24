# torch-029: Stable objectives, precision and mixed-precision boundaries

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-028`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. The central investigation is concrete: Exponentiate float32 logits 1000, 999 directly. The finish condition is both exponentials infinite. ValueError before loss evaluation. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. Logits 1000, 999 define a valid two-class distribution, but directly exponentiating them overflows common floating-point types. Subtracting a shared maximum before softmax preserves the distribution. CrossEntropyLoss and log sum exp implement stable combined operations that avoid unnecessary probability round trips.

Precision and range differ across float16, bfloat 16, float32 and float64. Automatic mixed precision selects operation dtypes under a backend policy; gradient scaling addresses underflow in certain training paths. Those mechanisms require hardware-specific validation. This default CPU lesson checks stable objectives and dtype limits without claiming GPU speed or a qualified mixed-precision training configuration. A stable loss can still optimize the wrong labels or denominator, so numerical and semantic checks remain separate.

## Design decisions and when to use this method

Use logits-aware objectives and numerically appropriate reductions before considering a lower-precision execution policy. Validate finite inputs and the intended class/reduction contract separately. More precision can reduce some arithmetic error, but it cannot repair an incorrect target, information leak or denominator.

Choose autocast and scaling only for an explicitly qualified device/operator workflow. The current CPU fixture checks arithmetic stability and dtype properties. It does not run or benchmark a mixed-precision training path, so GPU speed, overflow-recovery and convergence claims need additional evidence.

## Paired TensorFlow comparison

Compare [tf-029](../../deep-learning-tensorflow/guides/tf-029.md) after deriving the shared numerical contract.

TensorFlow and PyTorch provide stable logits-based objectives. Match dtype and reduction before comparison. Their mixed-precision policies and loss-scaling APIs differ, and a CPU arithmetic check does not qualify either framework's GPU training path.

## Vocabulary and concepts

**Overflow:** A result exceeding the numeric type's representable range.

**Log-sum-exp:** A stable logarithm of summed exponentials.

**Mixed precision:** A policy using different numeric types for different operations.

**Gradient scaling:** A technique changing gradient magnitude during certain low-precision training workflows.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-029/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-029.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-029.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use F.cross_entropy on raw logits and torch.logsumexp for a stable log normalizer. Inspect torch.isfinite on forward values and gradients. torch.finfo reports representable ranges and epsilon, but is not a performance benchmark. Keep dtype explicit in independent arithmetic comparisons. Do not cast arbitrary nonfinite inputs into a lower-precision type and expect a stable objective to repair them.

## Separate the mathematical distribution from its representation

For logits z=[1000, 999], the first-class probability is \(\frac{\exp(1000)}{\exp(1000)+\exp(999)}\). Dividing numerator and denominator by \(\exp(1000)\) gives \(\frac{1}{1+\exp(-1)}\), approximately 0.731059. The other probability is approximately 0.268941. The mathematical ratio is well defined even though directly materializing \(\exp(1000)\) overflows the types used in the counterexample.

More generally, subtracting the same finite m from every logit preserves softmax in exact arithmetic. Choosing \(m=\max(z)\) makes every shifted exponent at most one and at least one exactly one. For the target 0 loss, the shifted form is \(\log(1+\exp(-1))\), approximately 0.313262. The gradient is p-one_hot(target), or approximately[-0.268941, 0.268941]. Its entries sum to zero because a common logit shift does not change the objective. This gives an independent forward and backward contract.

Stability is more specific than a function name. logsumexp avoids raw exponential overflow, but computing a large logsumexp value and then subtracting a nearly equal large target logit can still lose precision. A fused logits loss or log_softmax formulation can preserve the small relative difference more directly. Similarly, computing a tiny probability and then taking its log can underflow where a direct log-probability calculation remains finite. Inspect intermediate representation rather than assuming algebraic equivalence implies equal floating-point error.

Range and precision are different properties:

| Type | Approximate maximum finite magnitude | Relative spacing near one |
| --- | --- | --- |
| float16 | 65, 504 | \({2}^{-10}\) |
| bfloat 16 | \(3.39\cdot {10}^{38}\) | \({2}^{-7}\) |
| float32 | \(3.4\cdot {10}^{38}\) | \({2}^{-23}\) |
| float64 | \(1.8\cdot {10}^{308}\) | \({2}^{-52}\) |

bfloat 16 has a much wider exponent range than float16 but fewer fraction bits. A value can avoid overflow while still be represented coarsely. Epsilon near one is not a universal absolute tolerance for all magnitudes or all algorithms. Summation length, conditioning, cancellation and the operations actually performed matter. [PyTorch 2.9 numerical accuracy](https://docs.pytorch.org/docs/2.9/notes/numerical_accuracy.html).

Shift invariance also has a finite-representation limit. If a huge common offset has already rounded two distinct logits to the same stored value, subtracting their maximum cannot recover the lost difference. The lesson's1000 and 999 remain distinct and are therefore an appropriate stability fixture. A NaN input is a different case: maximum subtraction does not repair it, and the explicit validator rejects it before evaluating the objective.

Autocast selects operation dtypes according to a backend policy. It is not equivalent to converting every model tensor and intermediate to float16. Some operations may run or accumulate in higher precision, while others use a lower-precision path. Eligibility and kernel behavior are device/version specific. A CPU bfloat 16 path and a CUDA float16 path therefore need separate acceptance rather than one generic mixed-precision label. [PyTorch 2.9 AMP](https://docs.pytorch.org/docs/2.9/amp.html).

Gradient scaling addresses another boundary. Multiplying a scalar loss by s multiplies its derivatives by s. An update workflow can compute those scaled derivatives, unscale them back to ordinary units, and detect nonfinite values before an optimizer step. This can protect some small backward values from underflow. It cannot recover information already lost in the forward pass or make an invalid loss meaningful.

Clipping thresholds must be applied to unscaled gradients if they are defined in ordinary gradient units. Otherwise changing the scale factor silently changes the effective clipping policy. A scaler may skip an optimizer update after detecting overflow; step counters, scheduler progression and logs should distinguish an attempted iteration from an actual parameter update. The scaler's own state belongs in a training checkpoint when it affects subsequent behavior.

A stable finite loss can still optimize the wrong example pairing, class index or reduction. Conversely, a finite forward value can have a problematic derivative at a singular or extreme point. Check forward inputs, loss, gradients and resulting parameter state as separate stages. The default examples retain small deterministic CPU work and make no throughput or accelerator-memory claim.

## Worked example / walkthrough

### Example A: Expose naive overflow

The underlying probabilities are well defined. The failure comes from an unstable intermediate representation, not an impossible classification task.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

logits=torch.tensor([1000.,999.],dtype=torch.float32); naive=torch.exp(logits)
assert torch.isinf(naive).all()
```

**Expected:** both exponentials infinite.

### Example B: Compute a stable class loss

The meaningful score difference is one. The stable combined objective avoids constructing enormous raw exponential values.

```python
stable=F.cross_entropy(logits[None,:],torch.tensor([0]))
np.testing.assert_allclose(stable.item(),np.log1p(np.exp(-1)),atol=1e-6,rtol=0)
```

**Expected:** loss \(\log(1+\exp(-1))\) within 1e-6.

### Example C: Check shift invariance

A common logit shift cancels from the normalizer. This property is useful for detecting wrong-axis or inconsistent-clipping implementations.

```python
torch.testing.assert_close(torch.softmax(logits,0),torch.softmax(torch.tensor([0.,-1.]),0),atol=1e-6,rtol=0)
```

**Expected:** probabilities match within 1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: both exponentials infinite. ValueError before loss evaluation. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Expose naive overflow.** Exponentiate float32 logits 1000, 999 directly.
   **Expected:** both exponentials infinite.
   **Verify:** Save the assertion results for exercise 1, including both exponentials infinite.

2. **Compute a stable class loss.** Use target 0 with the same logits.
   **Expected:** loss \(\log(1+\exp(-1))\) within 1e-6.
   **Verify:** Save the assertion results for exercise 2, including loss \(\log(1+\exp(-1))\) within 1e-6.

3. **Check shift invariance.** Compare softmax 1000, 999 with softmax 0, -1.
   **Expected:** probabilities match within 1e-6.
   **Verify:** Save the assertion results for exercise 3, including probabilities match within 1e-6.

4. **Inspect stable gradients.** Differentiate the target 0 loss with respect to both logits.
   **Expected:** finite gradients summing approximately 0.
   **Verify:** Save the assertion results for exercise 4, including finite gradients summing approximately 0.

5. **Compare dtype ranges explicitly.** Inspect float16 and bfloat 16 maximum values and float32 epsilon.
   **Expected:** bfloat 16 range exceeds float16; float32 epsilon positive.
   **Verify:** Save the assertion results for exercise 5, including bfloat 16 range exceeds float16; float32 epsilon positive.

6. **Reject a nonfinite input contract.** Pass aN aN logit through an explicit finite-input validator.
   **Expected:** ValueError before loss evaluation.
   **Verify:** Save the assertion results for exercise 6, including ValueError before loss evaluation.

## Common pitfalls and diagnosis

If exponentials overflow, inspect whether the implementation unnecessarily materialized them instead of using shifted logits or a fused objective. If the fused loss is finite but a manual logsumexp subtraction differs slightly, inspect cancellation and dtype before declaring the backend wrong. If a common shift destroys a score difference, check whether that difference was representable before softmax.

If a gradient becomes nonfinite, locate the first invalid stage rather than replacing every NaN with zero. If clipping behaves differently under scaling, verify that unscale precedes the threshold. If an AMP run appears faster, confirm equivalent outputs, actual update counts, warmup and the qualified device path. finfo metadata and a CPU arithmetic pass are not measurements of mixed-precision training performance.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Overflow, Log-sum-exp, Mixed precision using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-028` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does float64 eliminate all numerical problems?**

No. It offers more precision and range but still has finite limits and cannot repair an ill-conditioned algorithm or invalid input.

**Why separate arithmetic stability from task correctness?**

A perfectly finite loss can still use leaked data, wrong targets or an unintended reduction. Both contracts need independent checks.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-029, Stable objectives, precision and mixed-precision boundaries.
Read courses/deep-learning-pytorch/guides/torch-029.md and courses/deep-learning-pytorch/lessons/torch-029.py. Direct prerequisites: `torch-028`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
