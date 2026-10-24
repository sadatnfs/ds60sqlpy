"""tf-007: predict from the companion guide, then modify an owned copy."""

import tensorflow as tf

with tf.device("/CPU:0"):
    w = tf.Variable(0.0, dtype=tf.float64)
    with tf.GradientTape() as tape:
        loss = tf.square(w - 2.0)
    gradient = tape.gradient(loss, w)
assert gradient is not None
assert float(gradient.numpy()) == -4.0
print(float(loss.numpy()), float(gradient.numpy()))

with tf.device("/CPU:0"):
    precomputed = tf.square(w - 2.0)
    with tf.GradientTape() as tape:
        copied_loss = tf.identity(precomputed)
    missing = tape.gradient(copied_loss, w)
assert missing is None
print(missing)

# Exercise 1: Trace a recorded path
# Reproduce the connected scalar example and name which forward operations depend on w.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Distinguish a true zero
# Create a fresh Variable at w=2 and record the same loss computation.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Repair a missing path
# Reproduce the outside-scope calculation, then recompute the forward path inside a new
# tape.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Watch a constant deliberately
# Differentiate square(c-2) for a float64 constant c=0 with and without tape.watch(c).
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Preserve Variable identity
# Compare name rebinding after w-0.1*gradient with w.assign_sub on a fresh Variable.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Use a fresh recording
# Query an ordinary tape twice, then repeat the operation using a new tape. Also use
# constant feature x=2 with loss=(w*x-4)^2 at w=0.
# Add your attempt and keep its observed values or exception beside your prediction.
