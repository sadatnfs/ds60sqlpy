"""tf-023: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Expose a missing path
    w = tf.Variable(0.0, dtype=tf.float64)
    outside = (w - 2) ** 2
    with tf.GradientTape() as tape:
        loss = outside
    assert tape.gradient(loss, w) is None

    # Exercise 2: Distinguish an actual zero
    optimum = tf.Variable(2.0, dtype=tf.float64)
    with tf.GradientTape() as tape:
        loss = (optimum - 2) ** 2
    g = tape.gradient(loss, optimum)
    assert g is not None and float(g) == 0

    # Exercise 3: Repair two updates
    x = tf.constant([1.0, 2.0, 3.0], tf.float64)
    y = 2 * x
    w = tf.Variable(0.0, dtype=tf.float64)
    history = []
    for _ in range(2):
        with tf.GradientTape() as tape:
            loss = tf.reduce_mean((w * x - y) ** 2)
        g = tape.gradient(loss, w)
        assert g is not None
        w.assign_sub(0.1 * g)
        history.append(float(w))
    np.testing.assert_allclose(float(w), 448 / 225, atol=1e-12, rtol=0)

    # Exercise 4: Recompute loss after assignment
    after = float(tf.reduce_mean((w * x - y) ** 2))
    assert 0 <= after < 56 / 675

    # Exercise 5: Check gradient finiteness
    bad = tf.constant([2.0, 4.0, np.inf], tf.float64)
    saved = float(w)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean((w * x - bad) ** 2)
    g = tape.gradient(loss, w)
    assert not bool(tf.reduce_all(tf.math.is_finite(g))) and float(w) == saved

    # Exercise 6: Compare an analytic recurrence
    oracle = 0.0
    expected = []
    for _ in range(2):
        oracle -= 0.1 * (28 / 3) * (oracle - 2)
        expected.append(oracle)
    np.testing.assert_allclose(history, expected, atol=1e-12, rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
