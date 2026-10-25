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
    base = tf.Variable(tf.eye(4), trainable=False)
    a = tf.Variable(tf.ones((4, 1)) * 0.1)
    b = tf.Variable(tf.zeros((1, 4)))
    x = tf.ones((2, 4))
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.1)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(tf.matmul(x, base + tf.matmul(a, b))))
    gradients = tape.gradient(loss, [a, b])
    optimizer.apply_gradients(zip(gradients, [a, b], strict=True))
    tf.debugging.assert_all_finite(a, "a finite")
    tf.debugging.assert_all_finite(b, "b finite")
assert int(tf.size(a).numpy() + tf.size(b).numpy()) == 8
assert int(tf.size(base).numpy()) == 16
print("TensorFlow adapter census: base 16 frozen; trainable 8; base storage remains")
assert "GPU" in loss.device.upper(), "Expected actual GPU placement"
