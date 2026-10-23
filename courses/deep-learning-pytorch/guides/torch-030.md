# torch-030: Distributed gradients and accumulation semantics on CPU

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-029`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Distributed and accumulated gradients should represent a declared global objective. The central investigation is concrete: Combine means2, 6 with counts1, 3. The finish condition is global mean5; unweighted sha rd mean4. empty sha rd contributes0; global mean5. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Distributed and accumulated gradients should represent a declared global objective. Equal averaging of sha rd means weights shards equally, not examples. If one sha rd contains one observation with mean gradient2 and another contains three with mean6, the global example mean is5 rather than4. The same issue appears with unequal microbatches on one CPU.

To reproduce a full-batch mean through accumulation, hold parameters fixed while adding gradient sums, divide by the total active count, and apply one optimizer update. Stepping after each microbatch is a different trajectory because later gradients use changed weights. Distributed Data Parallel has its own reduction semantics; this lesson does not launch multiple processes or claim scaling. It derives the weighting rule that a real distributed implementation must preserve and explains which additional runtime evidence would be required.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-030](../../deep-learning-tensorflow/guides/tf-030.md) after deriving the shared numerical contract.

TensorFlow distributed strategies andPyTorchDDP can use different default reduction conventions. The paired CPU arithmetic establishes the intended example-weighted result; it does not demonstrate either backend's communication, scaling or failure behavior.

## Vocabulary and concepts

**Global objective:** The loss definition over all participating examples.

**Microbatch accumulation:** Combining derivatives before one parameter update.

**Sha rd weighting:** The rule assigning contributions from differently sized partitions.

**Distributed acceptance:** Actual multi-process behavior and failure evidence beyond scalar arithmetic.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-030/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-030.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-030.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use reduction='sum' for each microbatch, call backward without stepping, then divide accumulated gradients by the total count before one step. Clear gradients before starting the accumulation group. Count active masked targets when appropriate, not merely tensor storage size. If a distributed backend averages gradients across ranks, the local loss scaling must account for that reduction and unequal local counts.

## Worked example / walkthrough

### Example A: Weight unequal sha rd means

Each mean must be multiplied by its denominator to recover a sum. Averaging means directly discards that information.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

means=torch.tensor([2.,6.]); counts=torch.tensor([1.,3.])
assert (means*counts).sum().div(counts.sum()).item()==5 and means.mean().item()==4
```

**Expected:** global mean5; unweighted sha rd mean4.

### Example B: Reconstruct an example mean

The per-example vector is an independent oracle for the sha rd formula. It catches a checker that merely repeats a wrong averaging assumption.

```python
values=torch.tensor([2.,4.,6.,8.]); parts=[values[:1],values[1:]]
assert sum(part.sum() for part in parts).div(sum(part.numel() for part in parts)).item()==values.mean().item()==5
```

**Expected:** global mean5.

### Example C: Accumulate one full-batch gradient

The weight remains fixed across both backward calls. Accumulation is intentional here, and its denominator is applied exactly once.

```python
x=torch.arange(1,5,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
for start,end in [(0,1),(1,4)]: ((w*x[start:end]-y[start:end])**2).sum().backward()
w.grad.div_(4)
assert w.grad.item()==-30
oracle=torch.tensor(0.,dtype=torch.float64,requires_grad=True); full=((oracle*x-y)**2).mean(); assert torch.autograd.grad(full,oracle)[0].item()==-30
```

**Expected:** gradient-30, matching full-batch mean.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: global mean5; unweighted sha rd mean4. empty sha rd contributes0; global mean5. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Weight unequal sha rd means.** Combine means2, 6 with counts1, 3.
   **Expected:** global mean5; unweighted sha rd mean4.
   **Verify:** Save the assertion results for exercise 1, including global mean5; unweighted sha rd mean4.

2. **Reconstruct an example mean.** Split gradients2, 4, 6, 8 into one and three elements and recombine sums/counts.
   **Expected:** global mean5.
   **Verify:** Save the assertion results for exercise 2, including global mean5.

3. **Accumulate one full-batch gradient.** Atw0, usex1..4, y2 x, accumulate squared-loss sums forshards1 and3, and divide by 4.
   **Expected:** gradient-30, matching full-batch mean.
   **Verify:** Save the assertion results for exercise 3, including gradient-30, matching full-batch mean.

4. **Apply one accumulated update.** Take SGD.01 after the global gradient is formed.
   **Expected:** new weight.3.
   **Verify:** Save the assertion results for exercise 4, including new weight.3.

5. **Contrast separate microbatch updates.** Reset w0 and step after eachs hard mean instead.
   **Expected:** endpoint differs from.3.
   **Verify:** Save the assertion results for exercise 5, including endpoint differs from.3.

6. **Represent empty-sha rd contributions.** Combine an emptys hard and the four real gradients using sums and counts.
   **Expected:** empty sha rd contributes0; global mean5.
   **Verify:** Save the assertion results for exercise 6, including empty sha rd contributes0; global mean5.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Global objective, Microbatch accumulation, Sha rd weighting using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-029` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why is an average of means sometimes wrong?**

The groups may have different denominators. It gives equal group weight rather than equal example weight unless that is the intended objective.

**What remains untested after this CPU lesson?**

Actual process-group setup, collective ordering, uneven-input handling, cancellation, device behavior and throughput. Those require a separate distributed runtime experiment.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-030, Distributed gradients and accumulation semantics on CPU.
Read courses/deep-learning-pytorch/guides/torch-030.md and courses/deep-learning-pytorch/lessons/torch-030.py. Direct prerequisites: `torch-029`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
