"""tf-020: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Compare two reductions
    x = tf.constant([[[[1.0], [3.0]], [[2.0], [4.0]]]])
    assert float(tf.nn.max_pool2d(x, 2, 2, "VALID")[0, 0, 0, 0]) == 4
    assert float(tf.nn.avg_pool2d(x, 2, 2, "VALID")[0, 0, 0, 0]) == 2.5

    # Exercise 2: Inspect a flip
    flipped = tf.image.flip_left_right(x)
    np.testing.assert_array_equal(flipped.numpy().reshape(2, 2), [[3, 1], [4, 2]])

    # Exercise 3: Check an involution
    np.testing.assert_array_equal(tf.image.flip_left_right(flipped).numpy(), x.numpy())

    # Exercise 4: Expose discarded information
    altered = tf.constant([[[[0.0], [3.0]], [[2.0], [4.0]]]])
    assert float(tf.nn.max_pool2d(altered, 2, 2, "VALID")[0, 0, 0, 0]) == 4
    assert float(tf.nn.avg_pool2d(altered, 2, 2, "VALID")[0, 0, 0, 0]) == 2.25

    # Exercise 5: Keep evaluation deterministic
    def evaluate_image(value):
        return tf.identity(value)

    np.testing.assert_array_equal(evaluate_image(x).numpy(), x.numpy())
    np.testing.assert_array_equal(evaluate_image(x).numpy(), evaluate_image(x).numpy())

    # Exercise 6: Reject a semantic flip
    mirror = {"left": "right", "right": "left"}
    assert mirror["left"] == "right" and mirror[mirror["left"]] == "left"
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
