"""tf-008: read the companion guide, predict, then edit your own copy."""

from __future__ import annotations

import math

import tensorflow as tf


def gradient_step(rate=0.1, initial_weight=0.0):
    """Return four scalar observations for one paired three-point CPU update."""
    if isinstance(rate, bool) or isinstance(initial_weight, bool):
        raise TypeError("rate and initial_weight must be real scalars")
    rate, initial_weight = float(rate), float(initial_weight)
    if not math.isfinite(rate) or rate <= 0 or not math.isfinite(initial_weight):
        raise ValueError("positive finite rate and finite initial_weight required")
    with tf.device("/CPU:0"):
        x = tf.constant([1.0, 2.0, 3.0], dtype=tf.float64)
        y = tf.constant([2.0, 4.0, 6.0], dtype=tf.float64)
        weight = tf.Variable(initial_weight, dtype=tf.float64)
        with tf.GradientTape() as tape:
            prediction = weight * x
            loss = tf.reduce_mean(tf.square(prediction - y))
        gradient = tape.gradient(loss, weight)
        if gradient is None:
            raise ValueError("loss is disconnected from weight")
        before, grad = float(loss.numpy()), float(gradient.numpy())
        weight.assign_sub(tf.constant(rate, tf.float64) * gradient)
        after = tf.reduce_mean(tf.square(weight * x - y))
        return {
            "loss_before": before,
            "gradient": grad,
            "weight_after": float(weight.numpy()),
            "loss_after": float(after.numpy()),
        }


# Exercise 1: Trace the independent oracle
# Starting from the exact vectors and `w=0`, write the three residuals, loss, gradient and
# new weight for rate `0.1` before running Example A. Name which values are mutable.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 2: Find an overly large step
# Reset `w` to zero and change only the rate to `0.25`. Recompute the gradient from the
# reset state, apply one update and calculate the new loss. Explain whether subtraction of
# a gradient always improves a finite step.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 3: Construct two genuine steps
# Implement a two-step loop, with a fresh tape and forward computation on each iteration,
# starting at zero and rate `0.1`. Log the weight after each update and recompute each
# loss.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 4: Reject a broken pairing
# Write an eager helper that accepts only equal, nonempty vector shapes for `x` and `y`.
# It should reject the column target from Example B before calculating an MSE.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 5: Diagnose missing versus zero
# Compute `prediction=w*x` outside a tape, then use that precomputed tensor inside a new
# tape's loss. Inspect the gradient at `w=0`. Repair the recording boundary and separately
# test `w=2`.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 6: Transfer to a bias and held-out input
# A bias `b` adds the same offset to every prediction: `prediction=w*x+b`. Use targets
# `[3,5,7]`, initialize both scalars to zero and take one rate-`0.1` step. Keep
# `(x=4,y=9)` untouched until you inspect the resulting held-out prediction.
# Keep your prediction, code change and observed check in your own copy.

if __name__ == "__main__":
    print(gradient_step())
