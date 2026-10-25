"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

with tf.device(device):
    x = tf.constant([1.0, 2.0])
    y = tf.constant([2.0, 4.0])
    w = tf.Variable(0.0)
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.1)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(w * x - y))
    gradient = tape.gradient(loss, w)
    tf.debugging.assert_near(gradient, tf.constant(-10.0))
    optimizer.apply_gradients([(gradient, w)])
    tf.debugging.assert_near(w, tf.constant(1.0))
print("TensorFlow one-step weight:", float(w.numpy()), "device", w.device)
