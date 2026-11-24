# tf-020: explanatory solutions

Open these answers for Pooling and augmentation without label leakage after your own attempt at Example A, Compare two reductions, or after an explicit reveal. Each answer reuses the guide's literal inputs, so a mismatch points to one step. The companion script runs the assertions; this page explains why they test Pooling, Augmentation, Label invariance. After matching exercise 6, Reject a semantic flip, invent a new input without looking here.

## Mechanism review

Pooling summarizes a local region without fitting a separate coefficient at each position. Max pooling retains the largest response; average pooling retains the mean. These summaries discard information and therefore have different invariances. Augmentation changes training inputs under an assumption that the desired label remains the same. A horizontal flip may preserve the label of a symmetric shape but can change a left-pointing arrow into a right-pointing arrow. The validity of an augmentation comes from task semantics, not from the availability of a library transform. Evaluation must use a fixed policy so score changes are not concealed by random transformations.

**Pooling:** A local reduction that discards spatial detail.

**Augmentation:** A training transformation justified by label semantics.

**Label invariance:** The target remains valid after a transformation.

## Reading the implementation

max_pool2d and avg_pool2d reduce spatial patches in a four-dimensional image tensor. flip_left_right reverses the width axis while preserving batch, height and channels. Use literal arrays to inspect these axes. Training augmentation and evaluation transformation should be separate functions, with evaluation returning a known deterministic input representation.

## Exercise 1: Compare two reductions

The question is: Pool patch [[1, 3], [2, 4]] with a 2x2 window.

The max ignores the three smaller values, while the average uses every value equally. Equal output shapes do not mean equal retained information.

```python
x = tf.constant([[[[1.0], [3.0]], [[2.0], [4.0]]]])
assert float(tf.nn.max_pool2d(x, 2, 2, "VALID")[0, 0, 0, 0]) == 4
assert float(tf.nn.avg_pool2d(x, 2, 2, "VALID")[0, 0, 0, 0]) == 2.5
```

**Expected:** max 4; average 2.5.

**Verify:** In a fresh process, the exercise checks confirm `float(tf.nn.max_pool2d(x, 2, 2, 'VALID')[0, 0, 0, 0]) == 4` and `float(tf.nn.avg_pool2d(x, 2, 2, 'VALID')[0, 0, 0, 0]) == 2.5`.

## Exercise 2: Inspect a flip

The question is: Flip the patch horizontally and inspect every pixel.

The operation reverses columns, not rows. Naming the width axis prevents a mistaken vertical transformation from silently changing a directional task.

```python
flipped = tf.image.flip_left_right(x)
np.testing.assert_array_equal(flipped.numpy().reshape(2, 2), [[3, 1], [4, 2]])
```

**Expected:** rows [3, 1] and [4, 2].

**Verify:** In a fresh process, the exercise checks confirm `flipped.numpy().reshape(2, 2)` equals `[[3, 1], [4, 2]]`.

## Exercise 3: Check an involution

The question is: Flip twice and compare with the original image.

A horizontal flip is its own inverse. The round trip is a strong indexing check but does not prove that the intermediate image retained the original semantic label.

```python
np.testing.assert_array_equal(tf.image.flip_left_right(flipped).numpy(), x.numpy())
```

**Expected:** all pixels restored exactly.

**Verify:** In a fresh process, the exercise checks confirm `tf.image.flip_left_right(flipped).numpy()` equals `x.numpy()`.

## Exercise 4: Expose discarded information

The question is: Change the nonmaximum pixel 1 to 0 and recompute both pools.

The perturbation is invisible to max pooling. This helps explain why pooling creates robustness to some changes while also losing potentially useful detail.

```python
altered = tf.constant([[[[0.0], [3.0]], [[2.0], [4.0]]]])
assert float(tf.nn.max_pool2d(altered, 2, 2, "VALID")[0, 0, 0, 0]) == 4
assert float(tf.nn.avg_pool2d(altered, 2, 2, "VALID")[0, 0, 0, 0]) == 2.25
```

**Expected:** max still 4; average 2.25.

**Verify:** In a fresh process, the exercise checks confirm `float(tf.nn.max_pool2d(altered, 2, 2, 'VALID')[0, 0, 0, 0]) == 4` and `float(tf.nn.avg_pool2d(altered, 2, 2, 'VALID')[0, 0, 0, 0]) == 2.25`.

## Exercise 5: Keep evaluation deterministic

The question is: Define evaluation as an identity transform and compare repeated results with the source.

A deterministic evaluation path makes model comparisons interpretable. Random test augmentation would need a separately specified aggregation and uncertainty policy.

```python
def evaluate_image(value):
    return tf.identity(value)


np.testing.assert_array_equal(evaluate_image(x).numpy(), x.numpy())
np.testing.assert_array_equal(evaluate_image(x).numpy(), evaluate_image(x).numpy())
```

**Expected:** both evaluations equal the original patch.

**Verify:** In a fresh process, the exercise checks confirm `evaluate_image(x).numpy()` equals `x.numpy()` and `evaluate_image(x).numpy()` equals `evaluate_image(x).numpy()`.

## Exercise 6: Reject a semantic flip

The question is: Encode labels left and right and define the label change caused by horizontal reflection.

A reversible image transformation can still change the correct target. A valid training transform must either preserve the target or transform the target consistently, as this mapping demonstrates.

```python
mirror = {"left": "right", "right": "left"}
assert mirror["left"] == "right" and mirror[mirror["left"]] == "left"
```

**Expected:** left maps to right; retaining left is invalid.

**Verify:** In a fresh process, the exercise checks confirm `mirror['left'] == 'right'` and `mirror[mirror['left']] == 'left'`.

## Review after comparison

Change one fixture value in exercise 4, Expose discarded information, and predict the new result before running it. Keep the failing version of exercise 5, Keep evaluation deterministic, next to its repair. A missing framework is an environment record, not a failed assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
