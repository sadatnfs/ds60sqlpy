"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

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
