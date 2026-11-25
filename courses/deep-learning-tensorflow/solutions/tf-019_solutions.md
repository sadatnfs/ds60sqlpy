# tf-019: explanatory solutions

Open these answers after an attempt; they reuse the guide's inputs ([comparison steps](../STUDY-GUIDE.md#after-the-solutions)).

## Mechanism review

Convolutional layers reuse a small kernel at many positions. Each output sees a local patch, so the kernel has fewer parameters than an unconstrained map from every input pixel to every output pixel. TensorFlow applies cross-correlation: it slides the kernel without rotating it. A mathematical convolution would reverse spatial axes. Channels and batches add axes but do not change the basic local dot product. VALID padding includes only patches entirely inside the image; SAME padding inserts boundary values under a defined convention. The output shape depends on input size, kernel size, stride and padding, not on the apparent visual size of a plotted image.

**Kernel:** Shared weights applied to each local patch.

**Stride:** Distance between adjacent kernel positions.

**Receptive field:** Input positions that can influence an output.

## Reading the implementation

tf.nn.conv2d expects image shape (batch, height, width, channels) and filter shape (height, width, input_channels, output_channels). A 3x3 single-channel image and 2x2 kernel with stride 1 and VALID padding produce shape (1, 2, 2, 1). The first result is 1-5=-4. Rotating the kernel changes that sign. Keep the batch/channel singleton axes visible when checking shapes.

## Exercise 1: Detect a horizontal difference

The question is: Keep the 1..9 ramp image but use the kernel `[[1, -1], [0, 0]]`, which compares each pixel with its right neighbor. Predict the four VALID outputs before running it.

Moving one column to the right raises the ramp by 1, so every left-minus-right difference is -1. The diagonal kernel saw a step of 4 because it compared pixels one row and one column apart.

```python
horizontal = tf.reshape(tf.constant([1.0, -1.0, 0.0, 0.0]), (2, 2, 1, 1))
h = tf.nn.conv2d(image, horizontal, strides=1, padding="VALID")
np.testing.assert_array_equal(h.numpy().reshape(2, 2), np.full((2, 2), -1))
```

**Expected:** all four outputs -1.

**Verify:** In a fresh process, the exercise checks confirm `h.numpy().reshape(2, 2)` equals `np.full((2, 2), -1)`.

## Exercise 2: Predict SAME padding

The question is: Repeat the diagonal-kernel calculation with `padding='SAME'`. Predict the output shape and the nine values, remembering that TensorFlow pads a 2x2 kernel with zeros on the bottom and right.

The four interior positions match the VALID result. Along the right column and bottom row the subtracted neighbour is a padded zero, so the output equals the top-left pixel itself. Padding changes values at the border, not only the shape.

```python
same = tf.nn.conv2d(image, kernel, strides=1, padding="SAME")
assert tuple(same.shape) == (1, 3, 3, 1)
np.testing.assert_array_equal(same.numpy().reshape(3, 3), [[-4, -4, 3], [-4, -4, 6], [7, 8, 9]])
```

**Expected:** shape (1, 3, 3, 1); values [[-4, -4, 3], [-4, -4, 6], [7, 8, 9]].

**Verify:** In a fresh process, the exercise checks confirm `tuple(same.shape) == (1, 3, 3, 1)` and `same.numpy().reshape(3, 3)` equals `[[-4, -4, 3], [-4, -4, 6], [7, 8, 9]]`.

## Exercise 3: Count output positions

The question is: Compare VALID stride 1 and stride 2.

A larger stride visits fewer legal patch starts. Shape arithmetic is a useful first check before interpreting any learned filter values.

```python
assert tuple(out.shape) == (1, 2, 2, 1)
assert tuple(tf.nn.conv2d(image, kernel, strides=2, padding="VALID").shape) == (1, 1, 1, 1)
```

**Expected:** shapes (1, 2, 2, 1) and (1, 1, 1, 1).

**Verify:** In a fresh process, the exercise checks confirm `tuple(out.shape) == (1, 2, 2, 1)` and `tuple(tf.nn.conv2d(image, kernel, strides=2, padding='VALID').shape) == (1, 1, 1, 1)`.

## Exercise 4: Trace one pixel influence

The question is: Add 10 to the top-left image pixel and inspect which output changes.

The top-left pixel belongs only to the top-left valid patch. This controlled perturbation directly tests the local receptive field.

```python
changed_image = image.numpy().copy()
changed_image[0, 0, 0, 0] += 10
delta = tf.nn.conv2d(changed_image, kernel, strides=1, padding="VALID").numpy() - out.numpy()
np.testing.assert_array_equal(delta.reshape(2, 2), [[10, 0], [0, 0]])
```

**Expected:** only output [0, 0] increases 10.

**Verify:** In a fresh process, the exercise checks confirm `delta.reshape(2, 2)` equals `[[10, 0], [0, 0]]`.

## Exercise 5: Count shared parameters

The question is: Construct a bias-free Conv2D layer with 2 filters of size 2x2 on one input channel.

Each output channel has its own four kernel coefficients. Reusing the layer at more spatial locations increases computation but does not create a separate weight set for each location.

```python
layer = tf.keras.layers.Conv2D(2, 2, use_bias=False)
layer(image)
assert layer.count_params() == 8
```

**Expected:** 8 trainable scalars regardless of image height.

**Verify:** In a fresh process, the exercise checks confirm `layer.count_params() == 8`.

## Exercise 6: Add a constant image offset

The question is: Add 100 to every pixel and compare outputs under the zero-sum kernel.

The kernel coefficients sum to zero, so a constant offset cancels. This invariance belongs to this kernel; a general learned kernel need not preserve it.

```python
offset = tf.nn.conv2d(image + 100, kernel, strides=1, padding="VALID")
np.testing.assert_array_equal(offset.numpy(), out.numpy())
```

**Expected:** output unchanged.

**Verify:** In a fresh process, the exercise checks confirm `offset.numpy()` equals `out.numpy()`.

