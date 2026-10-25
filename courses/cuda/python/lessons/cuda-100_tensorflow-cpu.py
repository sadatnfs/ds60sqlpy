"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

with tf.device(device):
    q = tf.constant([[[1.0, 0.0], [0.0, 1.0]]])
    k = tf.identity(q)
    v = tf.constant([[[2.0, 3.0], [4.0, 5.0]]])
    scores = tf.matmul(q, k, transpose_b=True) / tf.sqrt(2.0)
    mask = tf.linalg.band_part(tf.ones((2, 2), dtype=tf.int32), -1, 0) > 0
    masked = tf.where(mask, scores, tf.constant(float("-inf")))
    weights = tf.nn.softmax(masked, axis=-1)
    actual = tf.matmul(weights, v)
    tf.debugging.assert_near(actual[:, 0, :], v[:, 0, :])
    tf.debugging.assert_near(tf.reduce_sum(weights, axis=-1), tf.ones((1, 2)))
print("TensorFlow causal attention:", actual.numpy().tolist(), "; no fused-backend claim")
