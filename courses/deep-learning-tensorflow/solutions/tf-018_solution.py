"""tf-018: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Update and inspect moving state
    epsilon = 1e-3
    values = tf.constant([[1., 3.], [3., 5.]])
    bn = tf.keras.layers.BatchNormalization(axis=-1, momentum=0.5, epsilon=epsilon)
    training_output = bn(values, training=True)
    np.testing.assert_allclose(bn.moving_mean.numpy(), [1, 2], atol=1e-6, rtol=0)
    np.testing.assert_allclose(bn.moving_variance.numpy(), [1, 1], atol=1e-6, rtol=0)
    expected = np.array([[-1., -1.], [1., 1.]]) / np.sqrt(1 + epsilon)
    np.testing.assert_allclose(training_output.numpy(), expected, atol=1e-6, rtol=0)
    probe = tf.keras.layers.BatchNormalization(axis=-1, momentum=0.5, epsilon=epsilon)
    probe(tf.constant([[0., 0.], [4., 4.]]), training=True)
    np.testing.assert_allclose(probe.moving_variance.numpy(), [2.5, 2.5], atol=1e-6, rtol=0)

    # Exercise 2: Freeze evaluation state
    epsilon = 1e-3
    values = tf.constant([[1., 3.], [3., 5.]])
    bn = tf.keras.layers.BatchNormalization(momentum=0.5, epsilon=epsilon)
    training_output = bn(values, training=True).numpy()
    mean_before = bn.moving_mean.numpy().copy()
    variance_before = bn.moving_variance.numpy().copy()
    evaluation = bn(values, training=False).numpy()
    expected = (values.numpy() - mean_before) / np.sqrt(variance_before + epsilon)
    np.testing.assert_allclose(evaluation, expected, atol=1e-6, rtol=0)
    np.testing.assert_array_equal(bn.moving_mean.numpy(), mean_before)
    np.testing.assert_array_equal(bn.moving_variance.numpy(), variance_before)
    assert not np.allclose(evaluation, training_output)

    # Exercise 3: Test LayerNorm row independence
    ln = tf.keras.layers.LayerNormalization(axis=-1, epsilon=1e-3)
    alone = ln(tf.constant([[1., 3.]])).numpy()[0]
    together = ln(tf.constant([[1., 3.], [100., 200.]])).numpy()[0]
    np.testing.assert_allclose(alone, together, atol=1e-6, rtol=0)
    np.testing.assert_allclose(alone, np.array([-1., 1.]) / np.sqrt(1.001), atol=1e-6, rtol=0)
    assert len(ln.non_trainable_variables) == 0

    # Exercise 4: Expose actual BatchNorm batch dependence
    small = np.array([[1., 3.], [3., 5.]], dtype=np.float32)
    large = np.vstack([small, [98., 199.]]).astype(np.float32)
    outputs = []
    for batch in [small, large]:
        layer = tf.keras.layers.BatchNormalization(momentum=0.5, epsilon=1e-3)
        observed = layer(tf.constant(batch), training=True).numpy()
        expected = (batch - batch.mean(axis=0, keepdims=True)) / np.sqrt(batch.var(axis=0, keepdims=True) + 1e-3)
        np.testing.assert_allclose(observed, expected, atol=1e-6, rtol=0)
        outputs.append(observed[0])
    assert not np.allclose(outputs[0], outputs[1])
    np.testing.assert_array_equal(large[0] - large.mean(axis=0), [-33, -66])

    # Exercise 5: Repeat updates and translate asymmetric momentum
    values = tf.constant([[1., 3.], [3., 5.]])
    bn = tf.keras.layers.BatchNormalization(momentum=0.5)
    bn(values, training=True)
    bn(values, training=True)
    np.testing.assert_allclose(bn.moving_mean.numpy(), [1.5, 3], atol=1e-6, rtol=0)
    asymmetric = tf.keras.layers.BatchNormalization(momentum=0.8)
    asymmetric(values, training=True)
    np.testing.assert_allclose(asymmetric.moving_mean.numpy(), [0.4, 0.8], atol=1e-6, rtol=0)
    asymmetric(values, training=True)
    np.testing.assert_allclose(asymmetric.moving_mean.numpy(), [0.72, 1.44], atol=1e-6, rtol=0)
    batch_mean = np.array([2., 4.])
    keras_first = (1 - 0.8) * batch_mean
    torch_same_number_formula = 0.8 * batch_mean
    torch_matched_formula = 0.2 * batch_mean
    assert not np.allclose(keras_first, torch_same_number_formula)
    np.testing.assert_allclose(keras_first, torch_matched_formula, atol=1e-12, rtol=0)

    # Exercise 6: Handle constant rows and frozen BatchNorm
    ln = tf.keras.layers.LayerNormalization(axis=-1, epsilon=1e-3)
    constant = ln(tf.constant([[5., 5.]])).numpy()
    assert np.isfinite(constant).all()
    np.testing.assert_allclose(constant, [[0, 0]], atol=1e-6, rtol=0)
    bn = tf.keras.layers.BatchNormalization(momentum=0.5, epsilon=1e-3)
    bn(tf.constant([[1., 3.], [3., 5.]]), training=True)
    bn.trainable = False
    before_mean = bn.moving_mean.numpy().copy()
    before_variance = bn.moving_variance.numpy().copy()
    probe = tf.constant([[100., 200.]])
    output = bn(probe, training=True).numpy()
    np.testing.assert_array_equal(bn.moving_mean.numpy(), before_mean)
    np.testing.assert_array_equal(bn.moving_variance.numpy(), before_variance)
    expected = (probe.numpy() - before_mean) / np.sqrt(before_variance + 1e-3)
    np.testing.assert_allclose(output, expected, atol=2e-5, rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
