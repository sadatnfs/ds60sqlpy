# torch-029: Stable objectives, precision and mixed-precision boundaries

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-028`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. The central investigation is concrete: Exponentiate float32 logits1000, 999 directly. The finish condition is both exponentials infinite. ValueError before loss evaluation. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. Logits1000, 999 define a valid two-class distribution, but directly exponentiating them overflows common floating-point types. Subtracting a shared maximum before softmax preserves the distribution. CrossEntropyLoss and log sum exp implement stable combined operations that avoid unnecessary probability round trips.

Precision and range differ across float16, bfloat16, float32 and float64. Automatic mixed precision selects operation dtypes under a backend policy; gradient scaling addresses underflow in certain training paths. Those mechanisms require hardware-specific validation. This default CPU lesson checks stable objectives and dtype limits without claiming GPU speed or a qualified mixed-precision training configuration. A stable loss can still optimize the wrong labels or denominator, so numerical and semantic checks remain separate.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-029](../../deep-learning-tensorflow/guides/tf-029.md) after deriving the shared numerical contract.

TensorFlow and PyTorch provide stable logits-based objectives. Match dtype and reduction before comparison. Their mixed-precision policies and loss-scaling APIs differ, and a CPU arithmetic check does not qualify either framework's GPU training path.

## Vocabulary and concepts

**Overflow:** A result exceeding the numeric type's represent able range.

**Log-sum-exp:** A stable logarithm of summed exponentials.

**Mixed precision:** A policy using different numeric types for different operations.

**Gradient scaling:** A technique changing gradient magnitude during certain low-precision training workflows.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-029/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-029.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-029.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

UseF.cross_entropy on raw logits and torch.log sum exp for a stable log normalizer. Inspect torch.isfinite on forward values and gradients. torch.finfo reports represent able ranges and epsilon, but is not a performance benchmark. Keep dtype explicit in independent arithmetic comparisons. Do not cast arbitrary nonfinite inputs into a lower-precision type and expect a stable objective to repair them.

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

**Expected:** loss log(1+exp(-1)) within1e-6.

### Example C: Check shift invariance

A common logit shift cancels from the normalizer. This property is useful for detecting wrong-axis or inconsistent-clipping implementations.

```python
torch.testing.assert_close(torch.softmax(logits,0),torch.softmax(torch.tensor([0.,-1.]),0),atol=1e-6,rtol=0)
```

**Expected:** probabilities match within1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: both exponentials infinite. ValueError before loss evaluation. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Expose naive overflow.** Exponentiate float32 logits1000, 999 directly.
   **Expected:** both exponentials infinite.
   **Verify:** Save the assertion results for exercise 1, including both exponentials infinite.

2. **Compute a stable class loss.** Use target0 with the same logits.
   **Expected:** loss log(1+exp(-1)) within1e-6.
   **Verify:** Save the assertion results for exercise 2, including loss log(1+exp(-1)) within1e-6.

3. **Check shift invariance.** Compare softmax1000, 999 with softmax0, -1.
   **Expected:** probabilities match within1e-6.
   **Verify:** Save the assertion results for exercise 3, including probabilities match within1e-6.

4. **Inspect stable gradients.** Differentiate the target0 loss with respect to both logits.
   **Expected:** finite gradients summing approximately0.
   **Verify:** Save the assertion results for exercise 4, including finite gradients summing approximately0.

5. **Compare dtype ranges explicitly.** Inspect float16 andbfloat16 maximum values and float32 epsilon.
   **Expected:** bfloat16 range exceeds float16; float32 epsilon positive.
   **Verify:** Save the assertion results for exercise 5, including bfloat16 range exceeds float16; float32 epsilon positive.

6. **Reject a nonfinite input contract.** Pass aN aN logit through an explicit finite-input validator.
   **Expected:** ValueError before loss evaluation.
   **Verify:** Save the assertion results for exercise 6, including ValueError before loss evaluation.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

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



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-029, Stable objectives, precision and mixed-precision boundaries.
Read courses/deep-learning-pytorch/guides/torch-029.md and courses/deep-learning-pytorch/lessons/torch-029.py. Direct prerequisites: `torch-028`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
