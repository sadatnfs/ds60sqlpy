"""Bounded TensorFlow lesson with explicit execution device."""

import tensorflow as tf

tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.set_visible_devices([], "GPU")
device = "/CPU:0"

dataset = (
    tf.data.Dataset.from_tensor_slices(tf.reshape(tf.range(8, dtype=tf.float32), (4, 2)))
    .batch(2)
    .prefetch(1)
)
options = tf.data.Options()
options.threading.private_threadpool_size = 1
dataset = dataset.with_options(options)
observed = []
for batch in dataset:
    with tf.device(device):
        values = tf.identity(batch)
        observed.extend(tf.reduce_sum(values, axis=1).numpy().tolist())
assert observed == [1.0, 5.0, 9.0, 13.0]
print("TensorFlow bounded input pipeline:", observed)
