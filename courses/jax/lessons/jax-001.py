"""Small offline JAX mechanism investigation; CPU evidence only."""

from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp

# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)


# Exercise 1: Trace another predictor
# Calculate predictions at weight 1, then their mean squared error.
def exercise_1():
    raise NotImplementedError("Trace another predictor")


# Exercise 2: Construct an exact fit
# Find a weight that matches every supplied target and verify it.
def exercise_2():
    raise NotImplementedError("Construct an exact fit")


# Exercise 3: Change the target
# Use targets [2,4,7] while keeping weight 2.
def exercise_3():
    raise NotImplementedError("Change the target")


# Exercise 4: Reject missing observations
# Define the behavior for two empty vectors.
def exercise_4():
    raise NotImplementedError("Reject missing observations")


# Exercise 5: Separate sum from mean
# Calculate the zero-weight sum of squared errors and compare it with three times the mean.
def exercise_5():
    raise NotImplementedError("Separate sum from mean")


# Exercise 6: Transfer to new inputs
# Evaluate weight 2 on inputs [4,5], then explain what a zero fixture error establishes.
def exercise_6():
    raise NotImplementedError("Transfer to new inputs")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
