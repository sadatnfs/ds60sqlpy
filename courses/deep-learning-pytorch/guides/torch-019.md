# torch-019: Convolutions, channel layouts and shared computation

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-018`.

## Learning objectives

Compute a Conv2d output by hand in NCHW layout, predict its output shape and count its shared parameters.

Central investigation: Apply the 2-by-2 kernel [[1, 0], [0, -1]] to a 3-by-3 ramp image, flip the kernel, change the stride and perturb one pixel.

Finish condition: The output has shape (1, 1, 2, 2) with every value -4, the flipped kernel gives +4, stride 2 gives shape (1, 1, 1, 1), a +10 top-left pixel changes only the top-left output, and the 1-to-2-channel 2-by-2 bias-free layer has 8 parameters.

## Purpose and mental model

Convolution applies a shared local kernel across spatial positions. PyTorch Conv2d expects NCHW layout: batch, channels, height, width. Its weight shape is output_channels, input_channels, kernel_height, kernel_width, which differs from the common TensorFlow NHWC image and HWIO kernel conventions. A legal reshape is not always a correct layout conversion; use permute to exchange the meaning of axes.

The operation is cross-correlation: the kernel slides without spatial rotation. VALID-style padding 0 includes only fully contained patches. Stride controls the gap between patch starts. The 3x3 ramp image and asymmetric 2x2 kernel produce an exact output of -4 at all four positions, making orientation and layout mistakes visible before introducing learned filters.

## Design decisions and when to use this method

Choose convolution when local structure and reuse of the same learned rule across positions are useful assumptions for the task. Decide the channel convention, boundary padding, stride and receptive-field growth before choosing a filter count. Weight sharing reduces parameters; it does not prove that a particular learned filter is useful or that the whole network is translation-invariant.

For a framework comparison, match the mathematical kernel and input axes before comparing values. Keep the literal ramp fixture as an arithmetic oracle, then use a nonuniform changed pixel to test locality. The CPU example establishes those small computations. It does not measure accelerator throughput or train an image classifier.

## Paired TensorFlow comparison

Compare [tf-019](../../deep-learning-tensorflow/guides/tf-019.md) after deriving the shared numerical contract.

TensorFlow's common `Conv2D` layout is NHWC with kernels HWIO; PyTorch uses NCHW and OIHW. Translate images with axis permutation and kernels with the corresponding permutation. Both use cross-correlation semantics despite the convolution name.

## Vocabulary and concepts

**NCHW:** Batch, channel, height, width axis order for PyTorch images.

**Shared kernel:** One weight pattern reused at many spatial locations.

**Receptive field:** Input positions capable of influencing an output.

**Cross-correlation:** Sliding a kernel without rotating it.

## How to run this lesson

Run `torch-019` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `kernel` and `image` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

Build image with shape (1, 1, 3, 3) and kernel (1, 1, 2, 2), then use `F.conv2d` with stride 1, padding 0. nn.Conv2d registers weight and optional bias. Count parameters as out_channels*in_channels*kernel_area plus bias entries. torch.flip(kernel, (-2, -1)) rotates both spatial axes for the convolution-versus-correlation counterexample.

## Derive the spatial map and its backward accumulation

Write a PyTorch image as X with shape (N, C_in, H, W) and a grouped Conv2d kernel as K with shape (C_out, \(\frac{C_{\mathrm{in}}}{g}\), k_H, k_W), where g is groups. For the ordinary \(g=1\) case, each output channel sums over every input channel and one spatial patch. With stride s, symmetric numeric padding p and dilation d on one axis, the effective kernel width is \(k_{\mathrm{eff}}=d(k-1)+1\) and the output width is \(\left\lfloor\frac{W+2p-k_{\mathrm{eff}}}{s}\right\rfloor+1\). Apply the same calculation independently to height. This is a count of valid kernel-start positions, not a statement that the image has been resized. [PyTorch 2.9 Conv2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Conv2d.html).

For \(W=H=3\), \(k=2\), \(d=1\), \(p=0\), \(s=1\), there are two starts on each axis. The tensor shape is therefore (1, 1, 2, 2). At the top-left start, the dot product is \(1\cdot 1+2\cdot 0+4\cdot 0+5\cdot (-1)=-4\). At the top-right start it is \(2-6=-4\). Equal outputs follow from this ramp and this kernel, not from a rule that every convolution outputs a constant. Stride 2 keeps only the start at zero and produces (1, 1, 1, 1).

Parameter count and evaluated output count are different. With two output channels, one input channel, a 2×2 kernel and no bias, there are \(2\cdot 1\cdot 2\cdot 2=8\) learned scalars regardless of spatial image size. Enabling bias adds one scalar per output channel, not one per output pixel. The same coefficient participates in multiple local dot products, so its gradient must accumulate contributions from all positions where it was used.

A separate analytic backward trace makes that sharing explicit. Suppose L is the sum of the four output values, so every upstream output derivative is one. Each kernel derivative is the sum of the corresponding input positions across the four patches:

| Kernel entry | Input values contributing | dL/dK |
| --- | --- | --- |
| top-left | 1, 2, 4, 5 | 12 |
| top-right | 2, 3, 5, 6 | 16 |
| bottom-left | 4, 5, 7, 8 | 24 |
| bottom-right | 5, 6, 8, 9 | 28 |

The input gradient, using the original kernel, is [[1, 1, 0], [1, 0, -1], [0, -1, -1]]. The center pixel participates in four patches, but its +1 and -1 contributions cancel while the other two coefficients are zero. A zero derivative at that pixel is therefore not a disconnected graph. Adding a trainable bias would give bias gradient four for this summed loss. These derivatives are an analytic extension of the fixture; the unchanged worked blocks test forward values and do not enable input/kernel autograd themselves.

Receptive fields grow through compositions. Start with jump \(j=1\) and field size \(r=1\). A layer updates r to r+(k_eff-1)j and j to js. Two stride-one 2×2 layers have a 3×3 receptive field, not 4×4. If the first 2×2 layer has stride 2, the second stride-one 2×2 layer sees a 4×4 input field because its adjacent inputs are already two original pixels apart. Padding affects which positions refer to actual data at the boundary.

Layout conversion must preserve these meanings. NCHW to NHWC uses permutation (0, 2, 3, 1); the inverse is (0, 3, 1, 2). A TensorFlow HWIO kernel becomes PyTorch OIHW with permutation (3, 2, 0, 1) for this ordinary convolution. A reshape with the same element count can produce legal dimensions while pairing the wrong channels or pixels. PyTorch channels_last memory format is yet another concept: it can change strides while the public tensor shape still uses NCHW semantics.

Both frameworks perform cross-correlation here. Rotating the asymmetric kernel changes the output to +4. A symmetric kernel could hide an accidental rotation; the asymmetric fixture exposes it. Weight sharing gives an equivariance relationship under suitable shifts and boundary assumptions, not unconditional invariance. Stride, padding and later reductions can break a simple shift correspondence. Likewise, the zero-sum kernel ignores a constant image offset on these VALID patches, but zero padding at edges or a different learned kernel changes that statement.

## Worked example / walkthrough

### Example A: Compute the fixed spatial filter

Each patch subtracts its bottom-right value from its top-left value. The difference is four throughout this ramp fixture.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

image = torch.arange(1, 10, dtype=torch.float64).reshape(1, 1, 3, 3)
kernel = torch.tensor([[[[1.0, 0.0], [0.0, -1.0]]]], dtype=torch.float64)
out = F.conv2d(image, kernel)
assert tuple(out.shape) == (1, 1, 2, 2)
torch.testing.assert_close(out, torch.full_like(out, -4), atol=0, rtol=0)
```

**Expected:** output shape 1, 1, 2, 2; all values -4.

### Example B: Rotate the kernel explicitly

An asymmetric kernel makes the convention observable. A symmetric kernel could hide an unintended rotation.

```python
rotated = torch.flip(kernel, (-2, -1))
changed = F.conv2d(image, rotated)
torch.testing.assert_close(changed, torch.full_like(changed, 4), atol=0, rtol=0)
```

**Expected:** all outputs +4.

### Example C: Translate image layout

Permutation changes axis meaning without inventing new values. Reshaping the element count alone would not implement a general layout translation.

```python
nhwc = image.permute(0, 2, 3, 1)
assert tuple(nhwc.shape) == (1, 3, 3, 1)
assert torch.equal(nhwc.permute(0, 3, 1, 2), image)
```

**Expected:** exact round trip; NHWC shape 1, 3, 3, 1.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Compute the fixed spatial filter. Predict exercise 6, Count shared parameters, from its prompt alone: Build a bias-free Conv2d with 1 input channel, 2 output channels and a 2-by-2 kernel. Then explain why this finish condition holds: The output has shape (1, 1, 2, 2) with every value -4, the flipped kernel gives +4, stride 2 gives shape (1, 1, 1, 1), a +10 top-left pixel changes only the top-left output, and the 1-to-2-channel 2-by-2 bias-free layer has 8 parameters. Keep each prediction beside the observed value.

## Exercises

1. **Apply a summing kernel.** Apply the 2-by-2 kernel of ones to the 3-by-3 image with values 1..9 in NCHW layout.
   **Expected:** outputs [[12, 16], [24, 28]] in shape (1, 1, 2, 2).
   **Verify:** In a fresh process, the exercise checks confirm `summed.tolist() == [[[[12.0, 16.0], [24.0, 28.0]]]]`.

2. **Predict the shape with padding.** Repeat the summing kernel with padding=1 and predict the output shape and its top-left value.
   **Expected:** shape (1, 1, 4, 4); top-left value 1.
   **Verify:** In a fresh process, the exercise checks confirm `tuple(padded_out.shape) == (1, 1, 4, 4)` and `padded_out[0, 0, 0, 0].item() == 1`.

3. **Permute a two-channel image.** Stack the image and its negative as two channels, convert NCHW to NHWC and read the channel pair at row 0, column 2.
   **Expected:** NHWC shape (1, 3, 3, 2); the pair is [3, -3].
   **Verify:** In a fresh process, the exercise checks confirm `tuple(channels_last.shape) == (1, 3, 3, 2)` and `channels_last[0, 0, 2].tolist() == [3.0, -3.0]`.

4. **Inspect stride output size.** Repeat with stride 2 and padding 0.
   **Expected:** output shape 1, 1, 1, 1.
   **Verify:** In a fresh process, the exercise checks confirm `tuple(F.conv2d(image, kernel, stride=2).shape) == (1, 1, 1, 1)`.

5. **Trace one pixel influence.** Add 10 to the top-left pixel and compare output delta.
   **Expected:** only top-left output increases 10.
   **Verify:** In a fresh process, the exercise checks confirm `delta[0, 0]` matches `torch.tensor([[10.0, 0.0], [0.0, 0.0]], dtype=torch.float64)` exactly.

6. **Count shared parameters.** Build a bias-free Conv2d with 1 input channel, 2 output channels and a 2-by-2 kernel.
   **Expected:** 8 trainable scalars.
   **Verify:** In a fresh process, the exercise checks confirm `sum((p.numel() for p in layer.parameters())) == 8`.

## Common pitfalls and diagnosis

If output dimensions differ, write the effective kernel and start-position count for each axis before changing tensor layout. If the shape agrees but values differ, calculate one patch with channel indices visible and check whether the kernel was rotated. If a TensorFlow comparison fails, verify both image and kernel permutations and the dtype before adjusting tolerances.

If a gradient differs by the number of positions, inspect whether shared contributions were summed or averaged by the loss. If only a center-pixel gradient is zero, check cancellation before diagnosing disconnection. A single changed corner pixel should influence only the outputs whose receptive fields include it. Keep stride, boundary and layout mistakes distinct: all can produce an accepted tensor operation with the wrong semantic result.

## Progressive hints

Hint 1: Example B (Rotate the kernel explicitly) alters one assumption of Example A (Compute the fixed spatial filter). Hint 2: exercise 4, Inspect stride output size, should end at output shape 1, 1, 1, 1. Work backward from it. Hint 3: exercise 5, Trace one pixel influence, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Translate image layout, from its inputs alone. Predict whether exercise 3, Permute a two-channel image, survives one changed input. Then explain NCHW, Shared kernel, Receptive field in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Compute the fixed spatial filter) cannot be rebuilt without help, revisit `torch-018` first. `torch-020` (Pooling, local augmentation and label invariants) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 Conv2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Conv2d.html), reviewed 2026-10-22 for the NCHW, Shared kernel, Receptive field behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Why is reshape insufficient for layout conversion?**

It changes how storage is grouped but does not generally move each semantic axis to its new position. Permute expresses the axis mapping explicitly.

**Does weight sharing guarantee translation invariance?**

No. Convolution is locally translation-equivariant under appropriate boundary conditions. Pooling, edges, strides and later layers affect the complete behavior.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-019, Convolutions, channel layouts and shared computation.
Read courses/deep-learning-pytorch/guides/torch-019.md and courses/deep-learning-pytorch/lessons/torch-019.py. Direct prerequisites: `torch-018`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
