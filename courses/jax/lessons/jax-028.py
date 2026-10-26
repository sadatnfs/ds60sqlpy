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


# Exercise 1: Check equal counts
# Combine sums [2,6] with counts [2,2].
def exercise_1():
    raise NotImplementedError("Check equal counts")


# Exercise 2: Add a zero-count participant
# Combine sums [2,12,0] with counts [1,3,0].
def exercise_2():
    raise NotImplementedError("Add a zero-count participant")


# Exercise 3: Gather participant identity
# All-gather scalar values [2,5] across the mapped axis.
def exercise_3():
    raise NotImplementedError("Gather participant identity")


# Exercise 4: Check a global sum
# Apply psum to participant values [2,5,7].
def exercise_4():
    raise NotImplementedError("Check a global sum")


# Exercise 5: Compile the collective model
# JIT the mapped weighted mean and compare its output.
def exercise_5():
    raise NotImplementedError("Compile the collective model")


# Exercise 6: Detect the wrong weighting
# Compare the mean of local gradient means with the correct global mean.
def exercise_6():
    raise NotImplementedError("Detect the wrong weighting")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
