"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

with tf.device(device):
    x = tf.Variable(tf.ones((8, 16)))
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(x))
    gradient = tape.gradient(loss, x)
    tf.debugging.assert_all_finite(gradient, "gradient must be finite")
logical_bytes = int(tf.size(x).numpy()) * x.dtype.size
assert logical_bytes == 512
print("TensorFlow input payload:", logical_bytes, "bytes; excludes gradient, context and reserve")
if device == "/GPU:0":
    print("TensorFlow allocator snapshot:", tf.config.experimental.get_memory_info("GPU:0"))
