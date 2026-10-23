# Worked solutions: planned pilot tf-008

Use these explanations after an honest attempt or an explicit request to
reveal a solution. The [learner guide](deep-learning-tensorflow-pilot.md)
contains the prediction, examples and six exercise contracts. Keep the
learner's own version beside this reference. These are design samples, not
active catalog artifacts or an automatic mastery check.

## Runtime and verification boundary

The runnable reference below needs the proposed, separately prepared
TensorFlow CPU profile. It uses float64 tensors, fixed local arrays and no
network, dataset, model download or GPU. Use the selected interpreter and the
Windows or POSIX run path in the learner guide. Do not install packages from
inside the solution.

The code blocks under Shared helpers and Exercises 1 through 6 form one Python
script in order. Run that script from a fresh process, so one exercise cannot
inherit a changed weight from an earlier notebook attempt. During this design
phase, the TensorFlow blocks were syntax-checked and their numbers checked
independently with exact rational arithmetic. TensorFlow itself was not
installed or executed. A future profile must pass these assertions on each
claimed platform before publication.

## Shared helpers

The denominator is the number of paired observations, not the number of
entries produced by an accidental broadcast. `assert_close` uses absolute
error only, so a default relative tolerance cannot weaken the small oracle.
The shape guard deliberately targets eager tensors in this lesson; it is not
a general symbolic Keras validation layer.

```python
import math
import tensorflow as tf

with tf.device("/CPU:0"):
    x = tf.constant([1.0, 2.0, 3.0], dtype=tf.float64)
    y = tf.constant([2.0, 4.0, 6.0], dtype=tf.float64)


def assert_close(actual, expected):
    assert math.isclose(float(actual), expected, rel_tol=0, abs_tol=1e-12)


def make_weight(value=0.0):
    with tf.device("/CPU:0"):
        return tf.Variable(value, dtype=tf.float64)


def paired_mse(prediction, target):
    if prediction.shape.rank != 1 or target.shape.rank != 1:
        raise ValueError("prediction and target must both be vectors")
    if prediction.shape != target.shape:
        raise ValueError("paired vectors must have equal shapes")
    if int(tf.size(prediction).numpy()) == 0:
        raise ValueError("paired vectors must be nonempty")
    return tf.reduce_mean(tf.square(prediction - target))


def recorded_gradient(weight):
    with tf.device("/CPU:0"), tf.GradientTape() as tape:
        prediction = weight * x
        loss = paired_mse(prediction, y)
    gradient = tape.gradient(loss, weight)
    if gradient is None:
        raise ValueError("loss is disconnected from weight")
    return loss, gradient


def one_step(rate):
    weight = make_weight()
    loss, gradient = recorded_gradient(weight)
    with tf.device("/CPU:0"):
        weight.assign_sub(tf.constant(rate, tf.float64) * gradient)
        after = paired_mse(weight * x, y)
    return tuple(float(value.numpy()) for value in (loss, gradient, weight, after))
```

## Exercise 1: trace the independent oracle

The loss as a function of the slope is
`L(w) = ((w-2)^2 + (2w-4)^2 + (3w-6)^2)/3 = (14/3)*(w-2)^2`.
Therefore `dL/dw = (28/3)*(w-2)`. At zero the gradient is negative: a small
increase in the slope reduces the loss locally. The supplied labels remain
fixed. Only the Variable representing the slope changes during an update.

The update is subtraction, so `0 - (1/10)*(-56/3) = 28/15`. Afterward the
residuals are `[-2/15,-4/15,-6/15]`, whose squared mean is `56/675`.

```python
before, gradient, weight, after = one_step(0.1)
assert_close(before, 56 / 3)
assert_close(gradient, -56 / 3)
assert_close(weight, 28 / 15)
assert_close(after, 56 / 675)
print("exercise 1:", before, gradient, weight, after)
```

**Expected:** all four assertions pass. **Verify:** compare the derivative
above with the tape value, not just with a copied printout. A negative gradient
is a direction statement at the old parameter, not a universal promise about
every possible step size.

## Exercise 2: find an overly large step

With rate `1/4`, the first gradient is unchanged because it is still computed
at zero. The new weight is `14/3`, past the optimum of 2. Its distance from the
optimum is `8/3`, so its loss is `(14/3)*(8/3)^2 = 896/27`. The model has made
a real update and still become worse.

```python
before, gradient, weight, after = one_step(0.25)
assert_close(gradient, -56 / 3)
assert_close(weight, 14 / 3)
assert_close(after, 896 / 27)
assert after > before
print("exercise 2:", weight, after)
```

**Expected:** the new loss exceeds `56/3`. **Verify:** the helper creates a
fresh zero-valued Variable; changing the rate on an already updated weight
would test a different experiment. The comparison should preserve the failed
large-step result rather than silently select a better rate afterward.

## Exercise 3: construct two genuine steps

Each tape records a forward computation at the current weight. After one
rate-`1/10` step, the distance from 2 is multiplied by `1/15`. The second
weight is `448/225` and its loss is `56/151875`. Reusing the first gradient
would instead add the same large update again; it would not differentiate the
new objective value.

```python
weight = make_weight()
weights, gradients, losses = [], [], []
for _ in range(2):
    loss, gradient = recorded_gradient(weight)
    gradients.append(float(gradient.numpy()))
    with tf.device("/CPU:0"):
        weight.assign_sub(tf.constant(0.1, tf.float64) * gradient)
        losses.append(float(paired_mse(weight * x, y).numpy()))
    weights.append(float(weight.numpy()))
assert_close(weights[0], 28 / 15)
assert_close(weights[1], 448 / 225)
assert_close(gradients[0], -56 / 3)
assert_close(gradients[1], -56 / 45)
assert_close(losses[1], 56 / 151875)
assert gradients[0] != gradients[1]
print("exercise 3:", weights, gradients, losses)
```

**Expected:** two different gradients and the two specified weights.
**Verify:** a new call to `recorded_gradient` creates a new tape and reads the
updated Variable. The logged post-update loss is recomputed; the old loss
returned by the tape still describes the old weight.

## Exercise 4: reject a broken pairing

At zero, broadcasting repeats each squared target across the input axis. Its
mean accidentally matches the correct loss. Its derivative uses every
input/target combination instead of matching records, yielding `-16`. A scalar
loss check alone cannot detect this pairing error.

```python
with tf.device("/CPU:0"):
    column_target = tf.reshape(y, (3, 1))
    zero = make_weight()
    with tf.GradientTape() as tape:
        wrong_residuals = zero * x - column_target
        wrong_loss = tf.reduce_mean(tf.square(wrong_residuals))
    wrong_gradient = tape.gradient(wrong_loss, zero)
    assert tuple(wrong_residuals.shape) == (3, 3)
    assert_close(wrong_loss.numpy(), 56 / 3)
    assert_close(wrong_gradient.numpy(), -16.0)
    assert_close(paired_mse(x, y).numpy(), 14 / 3)
    empty = tf.constant([], dtype=tf.float64)
    for left, right in ((x, column_target), (empty, empty)):
        try:
            paired_mse(left, right)
        except ValueError as error:
            assert "vector" in str(error) or "shape" in str(error)
        else:
            raise AssertionError("invalid pairing was accepted")
print("exercise 4: malformed and empty pairings rejected")
```

**Expected:** the valid vector pair succeeds and both invalid cases fail
before a mean is computed. **Verify:** keep the wrong-loss counterexample in
the evidence. Automatically flattening a target is inappropriate unless its
record ordering and intended meaning have been established separately.

## Exercise 5: diagnose missing versus zero

The first forward multiplication below happens outside the recording scope.
A later tape sees an already computed tensor and has no recorded path from
the loss to the Variable. `None` describes that missing path. At the true
optimum, the path exists and its derivative is the numeric value zero.

```python
weight = make_weight()
with tf.device("/CPU:0"):
    precomputed = weight * x
    with tf.GradientTape() as tape:
        disconnected_loss = paired_mse(precomputed, y)
    disconnected = tape.gradient(disconnected_loss, weight)
assert disconnected is None
_, repaired = recorded_gradient(weight)
assert_close(repaired.numpy(), -56 / 3)
optimum = make_weight(2.0)
_, zero_gradient = recorded_gradient(optimum)
assert zero_gradient is not None
assert_close(zero_gradient.numpy(), 0.0)
print("exercise 5:", disconnected, float(repaired.numpy()),
      float(zero_gradient.numpy()))
```

**Expected:** `None`, approximately `-18.666666666666668`, and `0.0`.
**Verify:** `is None` and a numeric comparison test different facts. Replacing
all missing gradients with zero hides disconnection bugs. Watching the
Variable after a forward computation also cannot retroactively record that
computation.

## Exercise 6: transfer to a bias and held-out input

At `w=b=0`, residuals are `[-3,-5,-7]`. Multiplying by `2*x` gives the slope
gradient `-68/3`; multiplying by 2 gives the bias gradient `-10`. Apply both
updates from that same old state. Do not update one parameter and recompute
the other gradient from a partially changed model.

The new predictions at the training inputs are `[49/15,83/15,117/15]`.
Subtracting `[3,5,7]` yields `[4/15,8/15,12/15]`, so training MSE is `224/675`.
The untouched point receives prediction `151/15`, with squared error `256/225`.

```python
weight, bias = make_weight(), make_weight()
with tf.device("/CPU:0"):
    shifted_y = tf.constant([3.0, 5.0, 7.0], dtype=tf.float64)
    with tf.GradientTape() as tape:
        loss = paired_mse(weight * x + bias, shifted_y)
    slope_gradient, bias_gradient = tape.gradient(loss, [weight, bias])
    assert slope_gradient is not None and bias_gradient is not None
    assert_close(slope_gradient.numpy(), -68 / 3)
    assert_close(bias_gradient.numpy(), -10)
    rate = tf.constant(0.1, dtype=tf.float64)
    weight.assign_sub(rate * slope_gradient)
    bias.assign_sub(rate * bias_gradient)
    training_mse = paired_mse(weight * x + bias, shifted_y)
    holdout_prediction = weight * tf.constant(4.0, tf.float64) + bias
    holdout_squared_error = tf.square(holdout_prediction - 9.0)
assert_close(weight.numpy(), 34 / 15)
assert_close(bias.numpy(), 1)
assert_close(training_mse.numpy(), 224 / 675)
assert_close(holdout_prediction.numpy(), 151 / 15)
assert_close(holdout_squared_error.numpy(), 256 / 225)
print("exercise 6:", float(training_mse.numpy()),
      float(holdout_prediction.numpy()), float(holdout_squared_error.numpy()))
```

**Expected:** every listed value passes absolute tolerance `1e-12`.
**Verify:** report training MSE and the one held-out squared error separately.
Their difference is not an estimate of population generalization. Changing the
rate after inspecting the holdout would turn that point into selection data;
a new untouched evaluation would then be needed.

## Retrieval, alternatives and evidence review

For the guide's fresh `x=[1,2], y=[3,6]` transfer at zero, the slope gradient is
`-15`. With rate `0.1`, the new weight is `1.5` and new MSE is `45/8`.
A teacher should change the fixture again before treating a memorized answer
as fresh evidence. A learner can also derive the quadratic directly, use a
finite difference away from a nondifferentiable point, or compare sum versus
mean reductions. Those methods are useful independent checks; none replaces
testing that TensorFlow recorded the intended path.

Use the guide's five-dimension rubric. Accept a different implementation when
it retains paired shapes, a fresh forward path for each step, explicit handling
of `None`, exact arithmetic checks and the evidence boundary. Ask the learner
to explain one wrong result and one new fixture without viewing this file.
Passing copied assertions is implementation evidence, not a certification.

## Sources and status

Reviewed **2026-10-22**: [TensorFlow autodiff](https://www.tensorflow.org/guide/autodiff)
explains the recording and gradient behavior. The numerical reference was
checked with standard-library rational arithmetic; the TensorFlow snippets
were syntax-checked only. Runtime/platform qualification is a future gate,
not a result established by this solution document.
