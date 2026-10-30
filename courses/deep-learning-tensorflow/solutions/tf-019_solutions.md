# tf-019: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Convolutional layers reuse a small kernel at many positions. Each output sees a local patch, so the kernel has fewer parameters than an unconstrained map from every input pixel to every output pixel. TensorFlow applies cross-correlation: it slides the kernel without rotating it. A mathematical convolution would reverse spatial axes. Channels and batches add axes but do not change the basic local dot product. VALID padding includes only patches entirely inside the image; SAME padding inserts boundary values under a defined convention. The output shape depends on input size, kernel size, stride and padding, not on the apparent visual size of a plotted image.

**Kernel:** Shared weights applied to each local patch.

**Stride:** Distance between adjacent kernel positions.

**Receptive field:** Input positions that can influence an output.

## Reading the implementation

tf.nn.conv2d expects image shape(batch,height,width,channels) and filter shape(height,width,input_channels,output_channels). A3x3 single-channel image and2x2 kernel with stride1 and VALID padding produce shape(1,2,2,1). The first result is1-5=-4. Rotating the kernel changes that sign. Keep the batch/channel singleton axes visible when checking shapes.

## Exercise 1: Compute local differences

The question is: Apply kernel[[1,0],[0,-1]] to the image1..9 arranged3x3.

Every patch has a bottom-right value four greater than its top-left value. The equal outputs are an arithmetic property of this ramp image, not a generic property of convolution.

```python
image = tf.reshape(tf.range(1, 10, dtype=tf.float32), (1, 3, 3, 1))
kernel = tf.reshape(tf.constant([1.0, 0.0, 0.0, -1.0]), (2, 2, 1, 1))
out = tf.nn.conv2d(image, kernel, strides=1, padding="VALID")
np.testing.assert_array_equal(out.numpy().reshape(2, 2), np.full((2, 2), -4))
```

**Expected:** all four outputs-4.

**Verify:** Compare the computed values or written argument with all four outputs-4.

## Exercise 2: Rotate the kernel

The question is: Reverse both spatial axes and repeat the calculation.

Kernel orientation distinguishes cross-correlation from mathematical convolution. A symmetric kernel would hide this difference, which is why the asymmetric diagonal kernel is useful.

```python
rot = tf.reverse(kernel, axis=[0, 1])
changed = tf.nn.conv2d(image, rot, strides=1, padding="VALID")
np.testing.assert_array_equal(changed.numpy().reshape(2, 2), np.full((2, 2), 4))
```

**Expected:** all outputs+4.

**Verify:** Compare the computed values or written argument with all outputs+4.

## Exercise 3: Count output positions

The question is: Compare VALID stride1 and stride2.

A larger stride visits fewer legal patch starts. Shape arithmetic is a useful first check before interpreting any learned filter values.

```python
assert tuple(out.shape) == (1, 2, 2, 1)
assert tuple(tf.nn.conv2d(image, kernel, strides=2, padding="VALID").shape) == (1, 1, 1, 1)
```

**Expected:** shapes(1,2,2,1) and(1,1,1,1).

**Verify:** Compare the computed values or written argument with shapes(1,2,2,1) and(1,1,1,1).

## Exercise 4: Trace one pixel influence

The question is: Add10 to the top-left image pixel and inspect which output changes.

The top-left pixel belongs only to the top-left valid patch. This controlled perturbation directly tests the local receptive field.

```python
changed_image = image.numpy().copy()
changed_image[0, 0, 0, 0] += 10
delta = tf.nn.conv2d(changed_image, kernel, strides=1, padding="VALID").numpy() - out.numpy()
np.testing.assert_array_equal(delta.reshape(2, 2), [[10, 0], [0, 0]])
```

**Expected:** only output[0,0] increases10.

**Verify:** Compare the computed values or written argument with only output[0,0] increases10.

## Exercise 5: Count shared parameters

The question is: Construct a bias-free Conv2D layer with2 filters of size2x2 on one input channel.

Each output channel has its own four kernel coefficients. Reusing the layer at more spatial locations increases computation but does not create a separate weight set for each location.

```python
layer = tf.keras.layers.Conv2D(2, 2, use_bias=False)
layer(image)
assert layer.count_params() == 8
```

**Expected:** 8 trainable scalars regardless of image height.

**Verify:** Compare the computed values or written argument with 8 trainable scalars regardless of image height.

## Exercise 6: Add a constant image offset

The question is: Add100 to every pixel and compare outputs under the zero-sum kernel.

The kernel coefficients sum to zero, so a constant offset cancels. This invariance belongs to this kernel; a general learned kernel need not preserve it.

```python
offset = tf.nn.conv2d(image + 100, kernel, strides=1, padding="VALID")
np.testing.assert_array_equal(offset.numpy(), out.numpy())
```

**Expected:** output unchanged.

**Verify:** Compare the computed values or written argument with output unchanged.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
