from __future__ import annotations

import math

import tensorflow as tf


def gradient_step(rate=0.1, initial_weight=0.0):
    """Return four scalar observations for one paired three-point CPU update."""
    if isinstance(rate, bool) or isinstance(initial_weight, bool):
        raise TypeError("rate and initial_weight must be real scalars")
    rate, initial_weight = float(rate), float(initial_weight)
    if not math.isfinite(rate) or rate <= 0 or not math.isfinite(initial_weight):
        raise ValueError("positive finite rate and finite initial_weight required")
    with tf.device("/CPU:0"):
        x = tf.constant([1.0, 2.0, 3.0], dtype=tf.float64)
        y = tf.constant([2.0, 4.0, 6.0], dtype=tf.float64)
        weight = tf.Variable(initial_weight, dtype=tf.float64)
        with tf.GradientTape() as tape:
            prediction = weight * x
            loss = tf.reduce_mean(tf.square(prediction - y))
        gradient = tape.gradient(loss, weight)
        if gradient is None:
            raise ValueError("loss is disconnected from weight")
        before, grad = float(loss.numpy()), float(gradient.numpy())
        weight.assign_sub(tf.constant(rate, tf.float64) * gradient)
        after = tf.reduce_mean(tf.square(weight * x - y))
        return {
            "loss_before": before,
            "gradient": grad,
            "weight_after": float(weight.numpy()),
            "loss_after": float(after.numpy()),
        }


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


def verify():
    # Exercise 1: exact reference checks
    before, gradient, weight, after = one_step(0.1)
    assert_close(before, 56 / 3)
    assert_close(gradient, -56 / 3)
    assert_close(weight, 28 / 15)
    assert_close(after, 56 / 675)
    print("exercise 1:", before, gradient, weight, after)

    # Exercise 2: exact reference checks
    before, gradient, weight, after = one_step(0.25)
    assert_close(gradient, -56 / 3)
    assert_close(weight, 14 / 3)
    assert_close(after, 896 / 27)
    assert after > before
    print("exercise 2:", weight, after)

    # Exercise 3: exact reference checks
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

    # Exercise 4: exact reference checks
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

    # Exercise 5: exact reference checks
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
    print("exercise 5:", disconnected, float(repaired.numpy()), float(zero_gradient.numpy()))

    # Exercise 6: exact reference checks
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
    print(
        "exercise 6:",
        float(training_mse.numpy()),
        float(holdout_prediction.numpy()),
        float(holdout_squared_error.numpy()),
    )

    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
