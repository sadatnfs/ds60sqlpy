"""tf-019: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Worked example A: Compute local differences
    image = tf.reshape(tf.range(1, 10, dtype=tf.float32), (1, 3, 3, 1))
    kernel = tf.reshape(tf.constant([1.0, 0.0, 0.0, -1.0]), (2, 2, 1, 1))
    out = tf.nn.conv2d(image, kernel, strides=1, padding="VALID")
    np.testing.assert_array_equal(out.numpy().reshape(2, 2), np.full((2, 2), -4))

    # Worked example B: Rotate the kernel on a steeper image
    steep = tf.reshape(
        tf.constant([0.0, 1.0, 2.0, 10.0, 11.0, 12.0, 20.0, 21.0, 22.0]), (1, 3, 3, 1)
    )
    rot = tf.reverse(kernel, axis=[0, 1])
    np.testing.assert_array_equal(
        tf.nn.conv2d(steep, kernel, strides=1, padding="VALID").numpy().reshape(2, 2),
        np.full((2, 2), -11),
    )
    changed = tf.nn.conv2d(steep, rot, strides=1, padding="VALID")
    np.testing.assert_array_equal(changed.numpy().reshape(2, 2), np.full((2, 2), 11))

    # Exercise 3: Count output positions
    assert tuple(out.shape) == (1, 2, 2, 1)
    assert tuple(tf.nn.conv2d(image, kernel, strides=2, padding="VALID").shape) == (1, 1, 1, 1)

    # Exercise 4: Trace one pixel influence
    changed_image = image.numpy().copy()
    changed_image[0, 0, 0, 0] += 10
    delta = tf.nn.conv2d(changed_image, kernel, strides=1, padding="VALID").numpy() - out.numpy()
    np.testing.assert_array_equal(delta.reshape(2, 2), [[10, 0], [0, 0]])

    # Exercise 5: Count shared parameters
    layer = tf.keras.layers.Conv2D(2, 2, use_bias=False)
    layer(image)
    assert layer.count_params() == 8

    # Exercise 6: Add a constant image offset
    offset = tf.nn.conv2d(image + 100, kernel, strides=1, padding="VALID")
    np.testing.assert_array_equal(offset.numpy(), out.numpy())

    # Exercise 1: Detect a horizontal difference
    horizontal = tf.reshape(tf.constant([1.0, -1.0, 0.0, 0.0]), (2, 2, 1, 1))
    h = tf.nn.conv2d(image, horizontal, strides=1, padding="VALID")
    np.testing.assert_array_equal(h.numpy().reshape(2, 2), np.full((2, 2), -1))

    # Exercise 2: Predict SAME padding
    same = tf.nn.conv2d(image, kernel, strides=1, padding="SAME")
    assert tuple(same.shape) == (1, 3, 3, 1)
    np.testing.assert_array_equal(same.numpy().reshape(3, 3), [[-4, -4, 3], [-4, -4, 6], [7, 8, 9]])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
