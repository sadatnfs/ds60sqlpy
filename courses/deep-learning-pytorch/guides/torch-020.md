# torch-020: Pooling, local augmentation and label invariants

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-019`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Pooling reduces local spatial information. The central investigation is concrete: Pool patch1, 3; 2, 4 with a2 x2 window. The finish condition is max4; average2.5. left->right->left. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Pooling reduces local spatial information. Max pooling retains the largest response; average pooling uses every entry. Both can make certain perturbations less visible while also discarding potentially useful details. Augmentation changes training inputs under a declared label policy. A horizontal flip may preserve a shape label but reverse a left/right direction label. A transform's availability in a library does not establish its validity for the task.

This lesson uses only torch operations on literal images, not torch vision or a data download. Training transforms and evaluation transforms are separate functions. Evaluation remains deterministic. Random augmentation, when introduced, should use the intended random state and be tested by invariants rather than a hard coded cross-platform mask.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-020](../../deep-learning-tensorflow/guides/tf-020.md) after deriving the shared numerical contract.

TensorFlow image operations commonly use channels-last layout, while these PyTorch examples use NCHW. The pooling and augmentation semantics are the same only after axis translation. This course does not assume torch vision; all fixtures are literal arrays.

## Vocabulary and concepts

**Pooling:** A local reduction discarding spatial detail.

**Augmentation:** A training transform with a declared target policy.

**Label invariance:** The condition that the target remains valid after a transform.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-020/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-020.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-020.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

F.max_pool2 d and avg_pool2 d operate on NCHW tensors. torch.flip(image, dims=(-1, )) reverses width, and flipping twice restores the original. A training flag or a separate transform object should decide whether augmentation applies. Inspect the label transformation beside the image:geometry alone cannot prove semantic invariance.

## Worked example / walkthrough

### Example A: Compare local reductions

The two operators retain different information despite identical output shape. The average uses all four values while the maximum ignores three smaller ones.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

image=torch.tensor([[[[1.,3.],[2.,4.]]]])
assert F.max_pool2d(image,2).item()==4 and F.avg_pool2d(image,2).item()==2.5
```

**Expected:** max4; average2.5.

### Example B: Inspect a horizontal flip

The last axis is the width under NCHW. Flipping the channel or height axis would be a different operation.

```python
flipped=torch.flip(image,dims=(-1,))
assert flipped[0,0].tolist()==[[3.,1.],[4.,2.]]
```

**Expected:** rows3, 1 and4, 2.

### Example C: Check the round trip

Reversibility is a useful indexing check, but does not prove the intermediate image has the original semantic label.

```python
assert torch.equal(torch.flip(flipped,dims=(-1,)),image)
```

**Expected:** exact original values.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: max4; average2.5. left->right->left. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compare local reductions.** Pool patch1, 3; 2, 4 with a2 x2 window.
   **Expected:** max4; average2.5.
   **Verify:** Save the assertion results for exercise 1, including max4; average2.5.

2. **Inspect a horizontal flip.** Flip the width axis and read the pixel s.
   **Expected:** rows3, 1 and4, 2.
   **Verify:** Save the assertion results for exercise 2, including rows3, 1 and4, 2.

3. **Check the round trip.** Flip the image horizontal l y twice.
   **Expected:** exact original values.
   **Verify:** Save the assertion results for exercise 3, including exact original values.

4. **Expose discarded information.** Change only the non maximum pixel1 to0 and compare pool s.
   **Expected:** max still4; average2.25.
   **Verify:** Save the assertion results for exercise 4, including max still4; average2.25.

5. **Keep evaluation transforms deterministic.** Define a transform that flips only in training and returns an owned copy in evaluation.
   **Expected:** evaluation equals source and does not alias it.
   **Verify:** Save the assertion results for exercise 5, including evaluation equals source and does not alias it.

6. **Transform directional labels consistently.** Map left to right under horizontal reflect i on and check the inverse.
   **Expected:** left->right->left.
   **Verify:** Save the assertion results for exercise 6, including left->right->left.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Pooling, Augmentation, Label invariance using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-019` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does a flip round trip prove augmentation validity?**

No. It proves the index operation is reversible. The task label can still change under the intermediate transform.

**Why separate training and evaluation transforms?**

Stochastic training changes are part of the fitting policy. Evaluation needs a declared repeatable policy so score changes are interpretable.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-020, Pooling, local augmentation and label invariants.
Read courses/deep-learning-pytorch/guides/torch-020.md and courses/deep-learning-pytorch/lessons/torch-020.py. Direct prerequisites: `torch-019`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
