"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

with tf.device(device):
    x = tf.Variable([2.0, -2.0], dtype=tf.float64)
    with tf.GradientTape() as tape:
        y = tf.reduce_sum(tf.nn.relu(2 * x + 1))
    gradient = tape.gradient(y, x)
    tf.debugging.assert_near(gradient, tf.constant([2.0, 0.0], dtype=tf.float64))
    eps = tf.constant(1e-5, dtype=tf.float64)
    numeric = (tf.nn.relu(2 * (x + eps) + 1) - tf.nn.relu(2 * (x - eps) + 1)) / (2 * eps)
    tf.debugging.assert_near(gradient, numeric, atol=1e-8, rtol=1e-8)
print("TensorFlow gradient reference:", gradient.numpy().tolist())
