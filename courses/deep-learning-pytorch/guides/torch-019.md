# torch-019: Convolutions, channel layouts and shared computation

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-018`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Convolution applies a shared local kernel across spatial positions. The central investigation is concrete: Apply kernel1, 0; 0, -1 to image1..9 in3 x3 NCHW layout. The finish condition is output shape1, 1, 2, 2; all values-4. 8 trainable scalars. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Convolution applies a shared local kernel across spatial positions. PyTorch C on v2 d expects NCHW layout:batch, channels, height, width. Its weight shape is output_channels, input_channels, kernel_height, kernel_width, which differs from the common TensorFlow NHWC image and HWIO kernel conventions. A legal reshape is not always a correct layout conversion; use permute to exchange the meaning of axes.

The operation is cross-correlation:the kernel slide s without spatial rotation. VALID-style padding0 includes only fully contained patches. Stride controls the gap between patch starts. The3 x3 ramp image and asymmetric2 x2 kernel produce an exact output of-4 at all four positions, making orientation and layout mistakes visible before introducing learned filters.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-019](../../deep-learning-tensorflow/guides/tf-019.md) after deriving the shared numerical contract.

TensorFlow's common C on v2 D layout is NHWC with kernels HWIO; PyTorch uses NCHW and OIHW. Translate images with axis permutation and kernels with the corresponding permutation. Both use cross-correlation semantics despite the convolution name.

## Vocabulary and concepts

**NCHW:** Batch, channel, height, width axis order for PyTorch images.

**Shared kernel:** One weight pattern reused at many spatial locations.

**Receptive field:** Input positions capable of influencing an output.

**Cross-correlation:** Sliding a kernel without r o t at in git.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-019/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-019.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-019.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Build image with shape(1, 1, 3, 3) and kernel(1, 1, 2, 2), then use F.conv2 d with stride1, padding0. nn.Conv2 d register s weight and optional bias. Count parameters as out_channels*in_channels*kernel_area plus bias entries. torch.flip(kernel, (-2, -1)) rotates both spatial axes for the convolution-versus-correlation counterexample.

## Worked example / walkthrough

### Example A: Compute the fixed spatial filter

Each patch subtracts its bottom-right value from its top-left value. The difference is four throughout this ramp fixture.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

image=torch.arange(1,10,dtype=torch.float64).reshape(1,1,3,3); kernel=torch.tensor([[[[1.,0.],[0.,-1.]]]],dtype=torch.float64)
out=F.conv2d(image,kernel)
assert tuple(out.shape)==(1,1,2,2); torch.testing.assert_close(out,torch.full_like(out,-4),atol=0,rtol=0)
```

**Expected:** output shape1, 1, 2, 2; all values-4.

### Example B: Rotate the kernel explicitly

An asymmetric kernel makes the convention observable. Asymmetric kernel could hide an unintended rotation.

```python
rotated=torch.flip(kernel,(-2,-1)); changed=F.conv2d(image,rotated)
torch.testing.assert_close(changed,torch.full_like(changed,4),atol=0,rtol=0)
```

**Expected:** all outputs+4.

### Example C: Translate image layout

Permutation changes axis meaning without inventing new values. Reshaping the element count alone would not implement a general layout translation.

```python
nhwc=image.permute(0,2,3,1); assert tuple(nhwc.shape)==(1,3,3,1)
assert torch.equal(nhwc.permute(0,3,1,2),image)
```

**Expected:** exact round trip; NHWC shape1, 3, 3, 1.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: output shape1, 1, 2, 2; all values-4. 8 trainable scalars. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compute the fixed spatial filter.** Apply kernel1, 0; 0, -1 to image1..9 in3 x3 NCHW layout.
   **Expected:** output shape1, 1, 2, 2; all values-4.
   **Verify:** Save the assertion results for exercise 1, including output shape1, 1, 2, 2; all values-4.

2. **Rotate the kernel explicitly.** Flip both kernel spatial axes and repeat.
   **Expected:** all outputs+4.
   **Verify:** Save the assertion results for exercise 2, including all outputs+4.

3. **Translate image layout.** Convert NCHW to NHWC with permute and back.
   **Expected:** exact round trip; NHWC shape1, 3, 3, 1.
   **Verify:** Save the assertion results for exercise 3, including exact round trip; NHWC shape1, 3, 3, 1.

4. **Inspect stride output size.** Repeat with stride2 and padding0.
   **Expected:** output shape1, 1, 1, 1.
   **Verify:** Save the assertion results for exercise 4, including output shape1, 1, 1, 1.

5. **Trace one pixel influence.** Add10 to the top-left pixel and compare output delta.
   **Expected:** only top-left output increases10.
   **Verify:** Save the assertion results for exercise 5, including only top-left output increases10.

6. **Count shared parameters.** Build a1-input-channel, 2-output-channel, 2 x2 bias-free C on v2 d.
   **Expected:** 8 trainable scalars.
   **Verify:** Save the assertion results for exercise 6, including 8 trainable scalars.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain NCHW, Shared kernel, Receptive field using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-018` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 Conv2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Conv2d.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why is reshape insufficient for layout conversion?**

It changes how storage is grouped but does not generally move each semantic axis to its new position. Permute expresses the axis mapping explicitly.

**Does weight sharing guarantee translation invariance?**

No. Convolution is locally translation-equivariant under appropriate boundary conditions. Pooling, edges, strides and later layers affect the complete behavior.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-019, Convolutions, channel layouts and shared computation.
Read courses/deep-learning-pytorch/guides/torch-019.md and courses/deep-learning-pytorch/lessons/torch-019.py. Direct prerequisites: `torch-018`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
