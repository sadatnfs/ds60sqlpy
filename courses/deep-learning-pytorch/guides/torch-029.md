# torch-029: Stable objectives, precision and mixed-precision boundaries

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-028`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Compute softmax losses stably and compare floating-point formats by their range and precision before choosing mixed precision.

Central investigation: Exponentiate float32 logits 1000 and 999 directly, then compute the same loss, probabilities and gradients with stable operations.

Finish condition: Direct exponentials overflow to infinity, the stable loss equals \(\log(1+\exp(-1))\) within 1e-6, shifted logits give probabilities that match within 1e-6, gradients are finite and sum to about 0, bfloat16 has a larger range than float16, and a NaN logit raises ValueError.

The worked examples demonstrate the mechanism; exercises 1-3 transfer it to new inputs and exercises 4-6 extend it to failures and boundary cases. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. Logits 1000, 999 define a valid two-class distribution, but directly exponentiating them overflows common floating-point types. Subtracting a shared maximum before softmax preserves the distribution. CrossEntropyLoss and logsumexp implement stable combined operations that avoid unnecessary probability round trips.

Precision and range differ across float16, bfloat16, float32 and float64. Automatic mixed precision selects operation dtypes under a backend policy; gradient scaling addresses underflow in certain training paths. Those mechanisms require hardware-specific validation. This default CPU lesson checks stable objectives and dtype limits without claiming GPU speed or a qualified mixed-precision training configuration. A stable loss can still optimize the wrong labels or denominator, so numerical and semantic checks remain separate.

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

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-029`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-029.py` under `.learning/expansion/torch-029/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use F.cross_entropy on raw logits and torch.logsumexp for a stable log normalizer. Inspect torch.isfinite on forward values and gradients. torch.finfo reports representable ranges and epsilon, but is not a performance benchmark. Keep dtype explicit in independent arithmetic comparisons. Do not cast arbitrary nonfinite inputs into a lower-precision type and expect a stable objective to repair them.

## Separate the mathematical distribution from its representation

For logits z=[1000, 999], the first-class probability is \(\frac{\exp(1000)}{\exp(1000)+\exp(999)}\). Dividing numerator and denominator by \(\exp(1000)\) gives \(\frac{1}{1+\exp(-1)}\), approximately 0.731059. The other probability is approximately 0.268941. The mathematical ratio is well defined even though directly materializing \(\exp(1000)\) overflows the types used in the counterexample.

More generally, subtracting the same finite m from every logit preserves softmax in exact arithmetic. Choosing \(m=\max(z)\) makes every shifted exponent at most zero, so every shifted exponential is at most one and at least one equals one. For the target 0 loss, the shifted form is \(\log(1+\exp(-1))\), approximately 0.313262. The gradient is p-one_hot(target), or approximately [-0.268941, 0.268941]. Its entries sum to zero because a common logit shift does not change the objective. This gives an independent forward and backward contract.

Stability is more specific than a function name. logsumexp avoids raw exponential overflow, but computing a large logsumexp value and then subtracting a nearly equal large target logit can still lose precision. A fused logits loss or log_softmax formulation can preserve the small relative difference more directly. Similarly, computing a tiny probability and then taking its log can underflow where a direct log-probability calculation remains finite. Inspect intermediate representation rather than assuming algebraic equivalence implies equal floating-point error.

Range and precision are different properties:

| Type | Approximate maximum finite magnitude | Relative spacing near one |
| --- | --- | --- |
| float16 | 65504 | \({2}^{-10}\) |
| bfloat16 | \(3.39\cdot {10}^{38}\) | \({2}^{-7}\) |
| float32 | \(3.4\cdot {10}^{38}\) | \({2}^{-23}\) |
| float64 | \(1.8\cdot {10}^{308}\) | \({2}^{-52}\) |

bfloat16 has a much wider exponent range than float16 but fewer fraction bits. A value can avoid overflow while still be represented coarsely. Epsilon near one is not a universal absolute tolerance for all magnitudes or all algorithms. Summation length, conditioning, cancellation and the operations actually performed matter. [PyTorch 2.9 numerical accuracy](https://docs.pytorch.org/docs/2.9/notes/numerical_accuracy.html).

Shift invariance also has a finite-representation limit. If a huge common offset has already rounded two distinct logits to the same stored value, subtracting their maximum cannot recover the lost difference. The lesson's 1000 and 999 remain distinct and are therefore an appropriate stability fixture. A NaN input is a different case: maximum subtraction does not repair it, and the explicit validator rejects it before evaluating the objective.

Autocast selects operation dtypes according to a backend policy. It is not equivalent to converting every model tensor and intermediate to float16. Some operations may run or accumulate in higher precision, while others use a lower-precision path. Eligibility and kernel behavior are device/version specific. A CPU bfloat16 path and a CUDA float16 path therefore need separate acceptance rather than one generic mixed-precision label. [PyTorch 2.9 AMP](https://docs.pytorch.org/docs/2.9/amp.html).

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

logits = torch.tensor([1000.0, 999.0], dtype=torch.float32)
naive = torch.exp(logits)
assert torch.isinf(naive).all()
```

**Expected:** both exponentials infinite.

### Example B: Compute a stable class loss

The meaningful score difference is one. The stable combined objective avoids constructing enormous raw exponential values.

```python
stable = F.cross_entropy(logits[None, :], torch.tensor([0]))
np.testing.assert_allclose(stable.item(), np.log1p(np.exp(-1)), atol=1e-6, rtol=0)
```

**Expected:** loss \(\log(1+\exp(-1))\) within 1e-6.

### Example C: Check shift invariance

A common logit shift cancels from the normalizer. This property is useful for detecting wrong-axis or inconsistent-clipping implementations.

```python
torch.testing.assert_close(
    torch.softmax(logits, 0), torch.softmax(torch.tensor([0.0, -1.0]), 0), atol=1e-6, rtol=0
)
```

**Expected:** probabilities match within 1e-6.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Expose naive overflow. Predict exercise 6, Reject a nonfinite input contract, from its prompt alone: Pass a NaN logit through an explicit finite-input validator. Then explain why this finish condition holds: Direct exponentials overflow to infinity, the stable loss equals \(\log(1+\exp(-1))\) within 1e-6, shifted logits give probabilities that match within 1e-6, gradients are finite and sum to about 0, bfloat16 has a larger range than float16, and a NaN logit raises ValueError. Keep each prediction beside the observed value.

## Exercises

1. **Find the float64 overflow boundary.** Exponentiate float64 values 709 and 710.
   **Expected:** \(e^{709}\) is finite (about 8.2e307); \(e^{710}\) overflows to inf.
   **Verify:** In a fresh process, the exercise checks confirm `torch.isfinite(grown[0])` and `torch.isinf(grown[1])`.

2. **Compute a stable loss for target 1.** Use float32 logits [1000, 998] with target class 1.
   **Expected:** loss \(\log(1+e^{2})\), about 2.1269, within 1e-5.
   **Verify:** In a fresh process, the exercise checks confirm `F.cross_entropy(wide_logits, torch.tensor([1])).item()` matches `np.log1p(np.exp(2))` within 1e-05.

3. **Check a new shift.** Compare the softmax of [1000, 998] with the softmax of [5, 3].
   **Expected:** both are about [0.8808, 0.1192] and match within 1e-6.
   **Verify:** In a fresh process, the exercise checks confirm `torch.softmax(wide_logits[0], 0)` matches `torch.softmax(torch.tensor([5.0, 3.0]), 0)` within 1e-06 and `torch.softmax(torch.tensor([5.0, 3.0]), 0)[0].item()` matches `1 / (1 + np.exp(-2))` within 1e-06.

4. **Inspect stable gradients.** Differentiate the target 0 loss with respect to both logits.
   **Expected:** finite gradients summing approximately 0.
   **Verify:** In a fresh process, the exercise checks confirm `torch.isfinite(values.grad).all()` and `values.grad.sum().item()` matches `0` within 1e-06.

5. **Compare dtype ranges explicitly.** Inspect float16 and bfloat16 maximum values and float32 epsilon.
   **Expected:** bfloat16 range exceeds float16; float32 epsilon positive.
   **Verify:** In a fresh process, the exercise checks confirm `torch.finfo(torch.bfloat16).max > torch.finfo(torch.float16).max` and `torch.finfo(torch.float32).eps > 0`.

6. **Reject a nonfinite input contract.** Pass a NaN logit through an explicit finite-input validator.
   **Expected:** ValueError before loss evaluation.
   **Verify:** In a fresh process, the exercise checks confirm `checked_loss(torch.tensor([[0.0, float('nan')]]), torch.tensor([0]))` raises `ValueError`.

## Common pitfalls and diagnosis

If exponentials overflow, inspect whether the implementation unnecessarily materialized them instead of using shifted logits or a fused objective. If the fused loss is finite but a manual logsumexp subtraction differs slightly, inspect cancellation and dtype before declaring the backend wrong. If a common shift destroys a score difference, check whether that difference was representable before softmax.

If a gradient becomes nonfinite, locate the first invalid stage rather than replacing every NaN with zero. If clipping behaves differently under scaling, verify that unscale precedes the threshold. If an AMP run appears faster, confirm equivalent outputs, actual update counts, warmup and the qualified device path. finfo metadata and a CPU arithmetic pass are not measurements of mixed-precision training performance.

## Progressive hints

Hint 1: Example B (Compute a stable class loss) alters one assumption of Example A (Expose naive overflow). Hint 2: exercise 4, Inspect stable gradients, should end at finite gradients summing approximately 0. Work backward from it. Hint 3: exercise 5, Compare dtype ranges explicitly, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Check shift invariance, from its inputs alone. Predict whether exercise 3, Check a new shift, survives one changed input. Then explain Overflow, Log-sum-exp, Mixed precision in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Expose naive overflow) cannot be rebuilt without help, revisit `torch-028` first. Otherwise keep your exercise 2 attempt, Compute a stable loss for target 1, as a regression case alongside a fresh transfer input, then continue along the course plan.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

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
