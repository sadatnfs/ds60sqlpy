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
assert "GPU" in w.device.upper(), "Expected actual GPU placement"
