"""tf-030: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Weight shard means
    means = np.array([2.0, 6.0])
    counts = np.array([1, 3])
    assert np.average(means, weights=counts) == 5 and means.mean() == 4

    # Exercise 2: Recover a full-batch mean
    g = np.array([2.0, 4.0, 6.0, 8.0])
    parts = [g[:1], g[1:]]
    recombined = sum(p.sum() for p in parts) / sum(len(p) for p in parts)
    assert recombined == g.mean() == 5

    # Exercise 3: Accumulate squared-loss gradients
    x = tf.constant([1.0, 2.0, 3.0, 4.0])
    y = 2 * x
    w = tf.Variable(0.0)
    with tf.GradientTape() as tape:
        full = tf.reduce_mean((w * x - y) ** 2)
    full_g = tape.gradient(full, w)
    total = 0.0
    for start, end in [(0, 1), (1, 4)]:
        with tf.GradientTape() as tape:
            summed = tf.reduce_sum((w * x[start:end] - y[start:end]) ** 2)
        total += float(tape.gradient(summed, w))
    assert float(full_g) == total / 4 == -30

    # Exercise 4: Apply exactly one update
    w.assign_sub(0.01 * (total / 4))
    np.testing.assert_allclose(float(w), 0.3, atol=1e-6, rtol=0)

    # Exercise 5: Expose per-batch updates
    other = tf.Variable(0.0)
    for start, end in [(0, 1), (1, 4)]:
        with tf.GradientTape() as tape:
            loss = tf.reduce_mean((other * x[start:end] - y[start:end]) ** 2)
        other.assign_sub(0.01 * tape.gradient(loss, other))
    assert abs(float(other) - 0.3) > 1e-6

    # Exercise 6: Handle an empty shard
    parts = [np.array([], dtype=float), g]
    count = sum(len(p) for p in parts)
    assert count == 4 and sum(p.sum() for p in parts) / count == 5
    assert sum(len(p) for p in [np.array([])]) == 0
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
