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
    x = tf.reshape(tf.constant([1.0, 2.0, 3.0, 4.0]), (1, 4, 1))
    kernel = tf.reshape(tf.constant([1.0, -1.0]), (2, 1, 1))
    y = tf.nn.conv1d(x, kernel, stride=1, padding="VALID")
    tf.debugging.assert_near(y, tf.fill((1, 3, 1), -1.0))
print("TensorFlow cross-correlation:", y.numpy().tolist())
assert "GPU" in y.device.upper(), "Expected actual GPU placement"
