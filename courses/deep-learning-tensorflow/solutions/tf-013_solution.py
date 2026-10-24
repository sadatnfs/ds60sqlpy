"""tf-013: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Convert scores
    z = tf.constant([-2.0, 0.0, 2.0])
    p = tf.math.sigmoid(z).numpy()
    assert p[1] == 0.5 and np.all(np.diff(p) > 0)

    # Exercise 2: Check the midpoint loss
    loss = tf.nn.sigmoid_cross_entropy_with_logits(
        labels=tf.constant([1.0]), logits=tf.constant([0.0])
    )
    np.testing.assert_allclose(loss.numpy(), [np.log(2)], atol=1e-6, rtol=0)

    # Exercise 3: Move the threshold
    assert (p >= 0.5).tolist() == [False, True, True]
    assert (p >= 0.8).tolist() == [False, False, True]

    # Exercise 4: Expose a convention mismatch
    wrong = float(
        tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant(1.0), logits=tf.constant(0.5))
    )
    assert abs(wrong - np.log(2)) > 0.1

    # Exercise 5: Stress large scores
    stable = tf.nn.sigmoid_cross_entropy_with_logits(
        labels=tf.constant([1.0, 0.0]), logits=tf.constant([1000.0, -1000.0])
    ).numpy()
    assert np.isfinite(stable).all()
    np.testing.assert_allclose(stable, [0, 0], atol=1e-6, rtol=0)

    # Exercise 6: Count decisions separately
    labels = np.array([0, 1, 1])
    assert np.count_nonzero((p >= 0.5) != labels) == 0
    assert np.count_nonzero((p >= 0.8) != labels) == 1
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
