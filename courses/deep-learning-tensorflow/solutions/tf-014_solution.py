"""tf-014: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Uniform class uncertainty
    logits = tf.zeros((1, 3))
    loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[1], logits=logits)
    np.testing.assert_allclose(loss.numpy(), [np.log(3)], atol=1e-6, rtol=0)

    # Exercise 2: Independent labels
    probs = tf.math.sigmoid(logits).numpy()
    np.testing.assert_array_equal(probs, [[0.5, 0.5, 0.5]])
    assert probs.sum() == 1.5

    # Exercise 3: Contrast target shapes
    sparse = np.array([2, 0], dtype=np.int32)
    multi = np.array([[1, 0, 1], [0, 1, 0]], dtype=np.float32)
    assert sparse.shape == (2,) and multi.shape == (2, 3)

    # Exercise 4: Verify softmax mass
    z = tf.constant([[2.0, 0.0, -2.0]])
    np.testing.assert_allclose(tf.nn.softmax(z).numpy().sum(), 1, atol=1e-6, rtol=0)
    np.testing.assert_allclose(tf.math.sigmoid(z).numpy().sum(), 1.5, atol=1e-6, rtol=0)

    # Exercise 5: Choose the denominator
    losses = tf.nn.sigmoid_cross_entropy_with_logits(
        labels=tf.constant(multi), logits=tf.zeros((2, 3))
    ).numpy()
    np.testing.assert_allclose(
        [losses.sum(), losses.mean()], [6 * np.log(2), np.log(2)], atol=1e-6, rtol=0
    )

    # Exercise 6: Reject an impossible class
    def validate_class(value):
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 3:
            raise ValueError("class index")
        return value

    assert validate_class(2) == 2
    try:
        validate_class(3)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted unknown class")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
