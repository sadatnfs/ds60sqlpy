# tf-011: explanatory solutions

Open these answers after an attempt; they reuse the guide's inputs ([comparison steps](../STUDY-GUIDE.md#after-the-solutions)).

## Mechanism review

Keras packages the same computation that the earlier tape lesson exposed. Dense computes a matrix product and optionally adds a bias. Compile selects the loss and optimizer but does not itself update weights. Training evaluates the forward function, reduces the loss, differentiates and applies the optimizer. To compare a high-level API with the hand-derived update, every relevant choice must match: no intercept, a zero initial weight, mean squared error, full-batch SGD and the same rate. Otherwise a difference may reflect a different model or objective instead of an API bug. Evaluation must be distinguished from a training call because it should not apply gradients.

**Dense:** An affine feature transformation with tracked weights.

**Compile:** Configuration of loss, optimizer and metrics.

**Training call:** Forward, differentiation and update on current weights.

## Reading the implementation

Input(shape=(1,)) excludes the batch dimension. Dense(1, use_bias=False) creates a single trainable scalar kernel. Reshape the three observations to (3, 1), matching targets exactly. Compile uses SGD(0.1) with loss='mse'. train_on_batch executes one full-batch step without a data-shuffle dependency. get_weights returns NumPy copies useful for comparison. A new model is required for each independent control. fit(x, y, epochs=1, batch_size=3, shuffle=False, verbose=0) runs the same full-batch step through the standard training loop and returns a History object whose loss entry is the mean loss computed during the epoch, before that epoch's update.

## Exercise 1: Fit one epoch with the standard loop

The question is: Build a fresh zero-initialized model, compile it with SGD(0.1) and loss='mse', then call fit(x, y, epochs=1, batch_size=3, shuffle=False, verbose=0).

With batch_size equal to the three observations and shuffle=False, one epoch is exactly one full-batch step, so fit must reproduce the hand-derived kernel. The History entry is the mean loss computed during the epoch, before the step changed the weight, which is why it reports 56/3 rather than the post-update loss 56/675. The relative tolerance reflects float32 rounding of a value near 18.7.

```python
fitted = tf.keras.Sequential(
    [
        tf.keras.Input(shape=(1,)),
        tf.keras.layers.Dense(1, use_bias=False, kernel_initializer="zeros"),
    ]
)
fitted.compile(optimizer=tf.keras.optimizers.SGD(0.1), loss="mse")
history = fitted.fit(x, y, epochs=1, batch_size=3, shuffle=False, verbose=0)
assert len(history.history["loss"]) == 1
np.testing.assert_allclose(history.history["loss"][0], 56 / 3, rtol=1e-6)
np.testing.assert_allclose(fitted.get_weights()[0], [[28 / 15]], atol=1e-6, rtol=0)
```

**Expected:** History loss 56/3 (the loss before the update); kernel 28/15, the same as train_on_batch.

**Verify:** In a fresh process, the exercise checks confirm `len(history.history['loss']) == 1`, `history.history['loss'][0]` matches `56 / 3` within relative tolerance 1e-6 and `fitted.get_weights()[0]` matches `[[28 / 15]]` within 1e-6.

## Exercise 2: Predict a halved learning rate

The question is: Before running it, predict the kernel and post-update loss for a fresh model trained once with SGD(0.05); then check the prediction.

The gradient at zero is still -56/3, so half the rate moves the kernel half as far, to 14/15. The loss is \((14/3)(w-2)^2\); with \(w-2=-16/15\) it equals 3584/675. A loss near 5.3 has larger float32 rounding than 56/675, so the check uses 1e-5.

```python
half = tf.keras.Sequential(
    [
        tf.keras.Input(shape=(1,)),
        tf.keras.layers.Dense(1, use_bias=False, kernel_initializer="zeros"),
    ]
)
half.compile(optimizer=tf.keras.optimizers.SGD(0.05), loss="mse")
half.train_on_batch(x, y)
np.testing.assert_allclose(half.get_weights()[0], [[14 / 15]], atol=1e-6, rtol=0)
np.testing.assert_allclose(np.mean((half(x).numpy() - y) ** 2), 3584 / 675, atol=1e-5, rtol=0)
```

**Expected:** kernel 14/15; post-update loss 3584/675, about 5.31.

**Verify:** In a fresh process, the exercise checks confirm `half.get_weights()[0]` matches `[[14 / 15]]` within 1e-6 and `np.mean((half(x).numpy() - y) ** 2)` matches `3584 / 675` within 1e-5.

## Exercise 3: Inspect forward shape

The question is: Pass two observations [[4], [5]] through the trained model and inspect output axes.

The leading dimension counts observations. Keeping the output column avoids broadcasting a vector target across a batch into a pairwise error matrix.

```python
pred = model(np.array([[4.0], [5.0]], dtype="float32")).numpy()
assert pred.shape == (2, 1)
np.testing.assert_allclose(pred[:, 0], [112 / 15, 28 / 3], atol=1e-6, rtol=0)
```

**Expected:** shape (2, 1), predictions 112/15 and 28/3.

**Verify:** In a fresh process, the exercise checks confirm `pred.shape == (2, 1)` and `pred[:, 0]` matches `[112 / 15, 28 / 3]` within 1e-6.

## Exercise 4: Evaluation leaves weights alone

The question is: Snapshot the kernel, run a forward evaluation with training=False, and compare.

A forward evaluation can calculate predictions without an optimizer step. More complex layers have training-dependent behavior, which is why explicitly passing the flag becomes important later.

```python
before = model.get_weights()[0].copy()
model(x, training=False)
np.testing.assert_array_equal(before, model.get_weights()[0])
```

**Expected:** kernel is exactly unchanged.

**Verify:** In a fresh process, the exercise checks confirm `before` equals `model.get_weights()[0]`.

## Exercise 5: Show the extra intercept

The question is: Construct an otherwise equivalent Dense layer with bias enabled and count trainable scalars.

A zero initial bias still has a gradient. Zero initialization does not freeze a parameter. Removing a parameter and initializing it to zero are different modeling decisions.

```python
with_bias = tf.keras.Sequential(
    [
        tf.keras.Input(shape=(1,)),
        tf.keras.layers.Dense(1, kernel_initializer="zeros", bias_initializer="zeros"),
    ]
)
assert with_bias.count_params() == 2
np.testing.assert_array_equal(with_bias.get_weights()[1], [0])
```

**Expected:** 2 parameters; bias starts 0.

**Verify:** In a fresh process, the exercise checks confirm `with_bias.count_params() == 2` and `with_bias.get_weights()[1]` equals `[0]`.

## Exercise 6: Compare the scalar oracle

The question is: Compute the first gradient directly from NumPy residuals and inputs, without Keras.

An independent formula guards against using two wrappers around the same broken calculation. The float32 tolerance reflects arithmetic precision and does not excuse a mismatched target shape.

```python
grad = 2 * np.mean((0 * x - y) * x)
np.testing.assert_allclose(grad, -56 / 3, atol=1e-6, rtol=0)
np.testing.assert_allclose(-0.1 * grad, 28 / 15, atol=1e-6, rtol=0)
```

**Expected:** gradient -56/3 and update 28/15.

**Verify:** In a fresh process, the exercise checks confirm `grad` matches `-56 / 3` within 1e-6 and `-0.1 * grad` matches `28 / 15` within 1e-6.

