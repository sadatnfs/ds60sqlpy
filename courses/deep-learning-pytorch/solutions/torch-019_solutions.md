# torch-019: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Convolution applies a shared local kernel across spatial positions. PyTorch Conv2d expects NCHW layout: batch, channels, height, width. Its weight shape is output_channels, input_channels, kernel_height, kernel_width, which differs from the common TensorFlow NHWC image and HWIO kernel conventions. A legal reshape is not always a correct layout conversion; use permute to exchange the meaning of axes.

The operation is cross-correlation: the kernel slides without spatial rotation. VALID-style padding 0 includes only fully contained patches. Stride controls the gap between patch starts. The 3 x3ramp image and asymmetric 2 x2kernel produce an exact output of-4at all four positions, making orientation and layout mistakes visible before introducing learned filters.

**NCHW:** Batch, channel, height, width axis order for PyTorch images.

**Shared kernel:** One weight pattern reused at many spatial locations.

**Receptive field:** Input positions capable of influencing an output.

**Cross-correlation:** Sliding a kernel without rotating it.

## Reading the implementation

Build image with shape(1, 1, 3, 3) and kernel(1, 1, 2, 2), then use F.conv 2 d with stride 1, padding 0. nn.Conv2d registers weight and optional bias. Count parameters as out_channels*in_channels*kernel_area plus bias entries. torch.flip(kernel, (-2, -1)) rotates both spatial axes for the convolution-versus-correlation counterexample.

## Derive the spatial map and its backward accumulation

Write a PyTorch image as X with shape(N, C_in, H, W) and a grouped Conv2d kernel as K with shape(C_out, C_in/g, k_H, k_W), where g is groups. For the ordinary g=1 case, each output channel sums over every input channel and one spatial patch. With stride s, symmetric numeric padding p and dilation d on one axis, the effective kernel width is k_eff=d(k-1)+1 and the output width is floor((W+2p-k_eff)/s)+1. Apply the same calculation independently to height. This is a count of valid kernel-start positions, not a statement that the image has been resized. [PyTorch 2.9 Conv2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Conv2d.html).

For W=H=3, k=2, d=1, p=0, s=1, there are two starts on each axis. The tensor shape is therefore(1, 1, 2, 2). At the top-left start, the dot product is 1×1+2×0+4×0+5×(-1)=-4. At the top-right start it is 2-6=-4. Equal outputs follow from this ramp and this kernel, not from a rule that every convolution outputs a constant. Stride 2 keeps only the start at zero and produces(1, 1, 1, 1).

Parameter count and evaluated output count are different. With two output channels, one input channel, a2×2 kernel and no bias, there are 2×1×2×2=8 learned scalars regardless of spatial image size. Enabling bias adds one scalar per output channel, not one per output pixel. The same coefficient participates in multiple local dot products, so its gradient must accumulate contributions from all positions where it was used.

A separate analytic backward trace makes that sharing explicit. Suppose L is the sum of the four output values, so every upstream output derivative is one. Each kernel derivative is the sum of the corresponding input positions across the four patches:

| Kernel entry | Input values contributing | dL/dK |
| --- | --- | --- |
| top-left | 1, 2, 4, 5 | 12 |
| top-right | 2, 3, 5, 6 | 16 |
| bottom-left | 4, 5, 7, 8 | 24 |
| bottom-right | 5, 6, 8, 9 | 28 |

The input gradient, using the original kernel, is[[1, 1, 0], [1, 0, -1], [0, -1, -1]]. The center pixel participates in four patches, but its +1 and -1 contributions cancel while the other two coefficients are zero. A zero derivative at that pixel is therefore not a disconnected graph. Adding a trainable bias would give bias gradient four for this summed loss. These derivatives are an analytic extension of the fixture; the unchanged worked blocks test forward values and do not enable input/kernel autograd themselves.

Receptive fields grow through compositions. Start with jump j=1 and field size r=1. A layer updates r to r+(k_eff-1)j and j to js. Two stride-one 2×2 layers have a 3×3 receptive field, not 4×4. If the first 2×2 layer has stride 2, the second stride-one 2×2 layer sees a 4×4 input field because its adjacent inputs are already two original pixels apart. Padding affects which positions refer to actual data at the boundary.

Layout conversion must preserve these meanings. NCHW to NHWC uses permutation(0, 2, 3, 1); the inverse is(0, 3, 1, 2). A TensorFlow HWIO kernel becomes PyTorch OIHW with permutation(3, 2, 0, 1) for this ordinary convolution. A reshape with the same element count can produce legal dimensions while pairing the wrong channels or pixels. PyTorch channels_last memory format is yet another concept: it can change strides while the public tensor shape still uses NCHW semantics.

Both frameworks perform cross-correlation here. Rotating the asymmetric kernel changes the output to+4. A symmetric kernel could hide an accidental rotation; the asymmetric fixture exposes it. Weight sharing gives an equivariance relationship under suitable shifts and boundary assumptions, not unconditional invariance. Stride, padding and later reductions can break a simple shift correspondence. Likewise, the zero-sum kernel ignores a constant image offset on these VALID patches, but zero padding at edges or a different learned kernel changes that statement.

## Exercise 1: Compute the fixed spatial filter

The question is: Apply kernel 1, 0; 0, -1 to image 1..9 in 3 x3NCHW layout.

Each patch subtracts its bottom-right value from its top-left value. The difference is four throughout this ramp fixture.

```python
image=torch.arange(1,10,dtype=torch.float64).reshape(1,1,3,3); kernel=torch.tensor([[[[1.,0.],[0.,-1.]]]],dtype=torch.float64)
out=F.conv2d(image,kernel)
assert tuple(out.shape)==(1,1,2,2); torch.testing.assert_close(out,torch.full_like(out,-4),atol=0,rtol=0)
```

**Expected:** output shape 1, 1, 2, 2; all values-4.

**Verify:** Compare the computed values or written argument with output shape 1, 1, 2, 2; all values-4.

## Exercise 2: Rotate the kernel explicitly

The question is: Flip both kernel spatial axes and repeat.

An asymmetric kernel makes the convention observable. A symmetric kernel could hide an unintended rotation.

```python
rotated=torch.flip(kernel,(-2,-1)); changed=F.conv2d(image,rotated)
torch.testing.assert_close(changed,torch.full_like(changed,4),atol=0,rtol=0)
```

**Expected:** all outputs+4.

**Verify:** Compare the computed values or written argument with all outputs+4.

## Exercise 3: Translate image layout

The question is: Convert NCHW to NHWC with permute and back.

Permutation changes axis meaning without inventing new values. Reshaping the element count alone would not implement a general layout translation.

```python
nhwc=image.permute(0,2,3,1); assert tuple(nhwc.shape)==(1,3,3,1)
assert torch.equal(nhwc.permute(0,3,1,2),image)
```

**Expected:** exact round trip; NHWC shape 1, 3, 3, 1.

**Verify:** Compare the computed values or written argument with exact round trip; NHWC shape 1, 3, 3, 1.

## Exercise 4: Inspect stride output size

The question is: Repeat with stride 2 and padding 0.

Only one fully contained patch start is visited in this small image. Output-size arithmetic should precede interpretation of feature maps.

```python
assert tuple(F.conv2d(image,kernel,stride=2).shape)==(1,1,1,1)
```

**Expected:** output shape 1, 1, 1, 1.

**Verify:** Compare the computed values or written argument with output shape 1, 1, 1, 1.

## Exercise 5: Trace one pixel influence

The question is: Add 10 to the top-left pixel and compare output delta.

The controlled perturbation demonstrates locality directly. A global normalization or other layer could introduce additional dependencies in a complete network.

```python
perturbed=image.clone(); perturbed[0,0,0,0]+=10; delta=F.conv2d(perturbed,kernel)-out
torch.testing.assert_close(delta[0,0],torch.tensor([[10.,0.],[0.,0.]],dtype=torch.float64),atol=0,rtol=0)
```

**Expected:** only top-left output increases 10.

**Verify:** Compare the computed values or written argument with only top-left output increases 10.

## Exercise 6: Count shared parameters

The question is: Build a1-input-channel, 2-output-channel, 2x2bias-free Conv2d.

Increasing image height creates more applications of the same kernel, not a separate weight set for each position.

```python
layer=nn.Conv2d(1,2,2,bias=False)
assert sum(p.numel() for p in layer.parameters())==8
```

**Expected:** 8trainable scalars.

**Verify:** Compare the computed values or written argument with 8trainable scalars.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
