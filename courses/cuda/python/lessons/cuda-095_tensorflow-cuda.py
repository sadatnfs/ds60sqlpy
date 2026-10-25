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
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(2,)),
            tf.keras.layers.Dense(1, use_bias=False),
            tf.keras.layers.Dropout(0.5),
        ]
    )
    model.layers[0].set_weights([tf.constant([[2.0], [-1.0]]).numpy()])
    y = model(tf.constant([[1.0, 3.0], [2.0, 1.0]]), training=False)
    tf.debugging.assert_near(y, tf.constant([[-1.0], [3.0]]))
print("TensorFlow evaluation output:", y.numpy().tolist())
assert "GPU" in y.device.upper(), "Expected actual GPU placement"
