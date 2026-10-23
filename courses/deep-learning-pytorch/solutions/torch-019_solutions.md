# torch-019: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Convolution applies a shared local kernel across spatial positions. PyTorch C on v2d expects NCHW layout:batch, channels, height, width. Its weight shape is output_channels, input_channels, kernel_height, kernel_width, which differs from the common TensorFlow NHWC image and HWIO kernel conventions. A legal reshape is not always a correct layout conversion; use permute to exchange the meaning of axes.

The operation is cross-correlation:the kernel slide s without spatial rotation. VALID-style padding0 includes only fully contained patches. Stride controls the gap between patch starts. The3x3ramp image and asymmetric2x2kernel produce an exact output of-4at all four positions, making orientation and layout mistakes visible before introducing learned filters.

**NCHW:** Batch, channel, height, width axis order for PyTorch images.

**Shared kernel:** One weight pattern reused at many spatial locations.

**Receptive field:** Input positions capable of influencing an output.

**Cross-correlation:** Sliding a kernel without r o t at in git.

## Reading the implementation

Build image with shape(1, 1, 3, 3) and kernel(1, 1, 2, 2), then use F.conv2d with stride1, padding0. nn.Conv2d register s weight and optional bias. Count parameters as out_channels*in_channels*kernel_area plus bias entries. torch.flip(kernel, (-2, -1)) rotates both spatial axes for the convolution-versus-correlation counterexample.

## Exercise 1: Compute the fixed spatial filter

The question is: Apply kernel1, 0; 0, -1 to image1..9 in3x3NCHW layout.

Each patch subtracts its bottom-right value from its top-left value. The difference is four throughout this ramp fixture.

```python
image=torch.arange(1,10,dtype=torch.float64).reshape(1,1,3,3); kernel=torch.tensor([[[[1.,0.],[0.,-1.]]]],dtype=torch.float64)
out=F.conv2d(image,kernel)
assert tuple(out.shape)==(1,1,2,2); torch.testing.assert_close(out,torch.full_like(out,-4),atol=0,rtol=0)
```

**Expected:** output shape1, 1, 2, 2; all values-4.

**Verify:** Compare the computed values or written argument with output shape1, 1, 2, 2; all values-4.

## Exercise 2: Rotate the kernel explicitly

The question is: Flip both kernel spatial axes and repeat.

An asymmetric kernel makes the convention observable. Asymmetric kernel could hide an unintended rotation.

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

**Expected:** exact round trip; NHWC shape1, 3, 3, 1.

**Verify:** Compare the computed values or written argument with exact round trip; NHWC shape1, 3, 3, 1.

## Exercise 4: Inspect stride output size

The question is: Repeat with stride2 and padding0.

Only one fully contained patch start is visited in this small image. Output-size arithmetic should precede interpretation of feature maps.

```python
assert tuple(F.conv2d(image,kernel,stride=2).shape)==(1,1,1,1)
```

**Expected:** output shape1, 1, 1, 1.

**Verify:** Compare the computed values or written argument with output shape1, 1, 1, 1.

## Exercise 5: Trace one pixel influence

The question is: Add10to the top-left pixel and compare output delta.

The controlled perturbation demonstrates locality directly. A global normalization or other layer could introduce additional dependencies in a complete network.

```python
perturbed=image.clone(); perturbed[0,0,0,0]+=10; delta=F.conv2d(perturbed,kernel)-out
torch.testing.assert_close(delta[0,0],torch.tensor([[10.,0.],[0.,0.]],dtype=torch.float64),atol=0,rtol=0)
```

**Expected:** only top-left output increases10.

**Verify:** Compare the computed values or written argument with only top-left output increases10.

## Exercise 6: Count shared parameters

The question is: Build a1-input-channel, 2-output-channel, 2x2bias-free C on v2d.

Increasing image height creates more applications of the same kernel, not a separate weight set for each position.

```python
layer=nn.Conv2d(1,2,2,bias=False)
assert sum(p.numel() for p in layer.parameters())==8
```

**Expected:** 8trainable scalars.

**Verify:** Compare the computed values or written argument with 8trainable scalars.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
