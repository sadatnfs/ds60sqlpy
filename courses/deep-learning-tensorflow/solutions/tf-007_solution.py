from __future__ import annotations

import math

import tensorflow as tf


def gradient_at(value):
    with tf.device("/CPU:0"):
        weight = tf.Variable(value, dtype=tf.float64)
        with tf.GradientTape() as tape:
            loss = tf.square(weight - 2.0)
        gradient = tape.gradient(loss, weight)
    if gradient is None:
        raise ValueError("recorded scalar path is disconnected")
    return float(loss.numpy()), float(gradient.numpy())


def verify():
    # Exercise 1: connected scalar path
    assert gradient_at(0.0) == (4.0, -4.0)
    # Exercise 2: a genuine connected zero
    assert gradient_at(2.0) == (0.0, 0.0)
    with tf.device("/CPU:0"):
        weight = tf.Variable(0.0, dtype=tf.float64)
        # Exercise 3: outside recording versus repaired forward
        precomputed = tf.square(weight - 2.0)
        with tf.GradientTape() as tape:
            copied = tf.identity(precomputed)
        assert tape.gradient(copied, weight) is None
        # Exercise 4: a constant must be watched explicitly
        constant = tf.constant(0.0, dtype=tf.float64)
        with tf.GradientTape() as tape:
            loss = tf.square(constant - 2.0)
        assert tape.gradient(loss, constant) is None
        with tf.GradientTape() as tape:
            tape.watch(constant)
            loss = tf.square(constant - 2.0)
        assert float(tape.gradient(loss, constant).numpy()) == -4.0
        # Exercise 5: assignment keeps the mutable object
        old = weight
        rebound = weight - tf.constant(0.1, tf.float64) * (-4.0)
        assert not isinstance(rebound, tf.Variable) and float(old.numpy()) == 0
        weight.assign_sub(tf.constant(0.1, tf.float64) * (-4.0))
        assert weight is old and math.isclose(float(weight.numpy()), 0.4, rel_tol=0, abs_tol=1e-12)
        # Exercise 6: fresh tape and constant-feature dependence
        weight.assign(0.0)
        with tf.GradientTape() as tape:
            loss = tf.square(weight - 2.0)
        assert float(tape.gradient(loss, weight).numpy()) == -4.0
        try:
            tape.gradient(loss, weight)
        except RuntimeError:
            pass
        else:
            raise AssertionError("consumed tape accepted second gradient query")
        with tf.GradientTape() as fresh:
            feature_loss = tf.square(weight * 2.0 - 4.0)
        assert float(fresh.gradient(feature_loss, weight).numpy()) == -16.0
    return {"loss": 4.0, "gradient": -4.0, "optimum_gradient": 0.0}


if __name__ == "__main__":
    print(verify())
