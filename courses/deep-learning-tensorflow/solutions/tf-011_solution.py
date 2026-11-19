"""tf-011: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Worked example A: Construct a scalar model
    model = tf.keras.Sequential(
        [
            tf.keras.Input(shape=(1,)),
            tf.keras.layers.Dense(1, use_bias=False, kernel_initializer="zeros"),
        ]
    )
    x = np.array([[1.0], [2.0], [3.0]], dtype="float32")
    y = 2 * x
    assert model.count_params() == 1
    np.testing.assert_array_equal(model(x).numpy(), np.zeros((3, 1)))

    # Worked example B: Audit the first update
    model.compile(optimizer=tf.keras.optimizers.SGD(0.1), loss="mse")
    model.train_on_batch(x, y)
    np.testing.assert_allclose(model.get_weights()[0], [[28 / 15]], atol=1e-6, rtol=0)
    np.testing.assert_allclose(np.mean((model(x).numpy() - y) ** 2), 56 / 675, atol=1e-6, rtol=0)

    # Exercise 3: Inspect forward shape
    pred = model(np.array([[4.0], [5.0]], dtype="float32")).numpy()
    assert pred.shape == (2, 1)
    np.testing.assert_allclose(pred[:, 0], [112 / 15, 28 / 3], atol=1e-6, rtol=0)

    # Exercise 4: Evaluation leaves weights alone
    before = model.get_weights()[0].copy()
    model(x, training=False)
    np.testing.assert_array_equal(before, model.get_weights()[0])

    # Exercise 5: Show the extra intercept
    with_bias = tf.keras.Sequential(
        [
            tf.keras.Input(shape=(1,)),
            tf.keras.layers.Dense(1, kernel_initializer="zeros", bias_initializer="zeros"),
        ]
    )
    assert with_bias.count_params() == 2
    np.testing.assert_array_equal(with_bias.get_weights()[1], [0])

    # Exercise 6: Compare the scalar oracle
    grad = 2 * np.mean((0 * x - y) * x)
    np.testing.assert_allclose(grad, -56 / 3, atol=1e-6, rtol=0)
    np.testing.assert_allclose(-0.1 * grad, 28 / 15, atol=1e-6, rtol=0)

    # Exercise 1: Fit one epoch with the standard loop
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

    # Exercise 2: Predict a halved learning rate
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
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
