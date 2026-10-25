"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

with tf.device(device):
    w = tf.Variable(1.0)
    velocity = tf.Variable(0.0)

    def step():
        with tf.GradientTape() as tape:
            loss = tf.square(w)
        gradient = tape.gradient(loss, w)
        velocity.assign(0.9 * velocity + gradient)
        w.assign_sub(0.1 * velocity)

    step()
    step()
    saved_weight, saved_velocity = tf.identity(w), tf.identity(velocity)
    step()
    expected = tf.identity(w)
    w.assign(saved_weight)
    velocity.assign(saved_velocity)
    step()
    tf.debugging.assert_near(w, expected)
print("TensorFlow in-memory momentum continuation:", float(w.numpy()))
