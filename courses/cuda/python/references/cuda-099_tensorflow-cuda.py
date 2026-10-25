"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
if not tf.test.is_built_with_cuda() or not tf.config.list_physical_devices("GPU"):
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
for gpu_device in tf.config.list_physical_devices("GPU"):
    tf.config.experimental.set_memory_growth(gpu_device, True)
device = "/GPU:0"

with tf.device(device):
    x = tf.constant([1.0, 2.0, 3.0, 4.0])
    y = 2 * x
    w = tf.Variable(0.0)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(w * x - y))
    full = tape.gradient(loss, w)
    accumulated = tf.constant(0.0)
    for a, b in [(x[:3], y[:3]), (x[3:], y[3:])]:
        with tf.GradientTape() as tape:
            micro_loss = tf.reduce_sum(tf.square(w * a - b)) / 4.0
        accumulated += tape.gradient(micro_loss, w)
    tf.debugging.assert_near(full, accumulated)
print("TensorFlow unequal microbatch gradient:", float(accumulated.numpy()))
assert "GPU" in accumulated.device.upper(), "Expected actual GPU placement"
