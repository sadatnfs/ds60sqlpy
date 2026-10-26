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


# Exercise 1: Replay initialization
# Initialize twice from the same key and compare every leaf.
def exercise_1():
    raise NotImplementedError("Replay initialization")


# Exercise 2: Inspect gradients
# Differentiate the training objective at initialization.
def exercise_2():
    raise NotImplementedError("Inspect gradients")


# Exercise 3: Check one compiled update
# Compare one eager step and one compiled step from identical state.
def exercise_3():
    raise NotImplementedError("Check one compiled update")


# Exercise 4: Evaluate untouched inputs
# Calculate loss at the two held-out interpolation points after the fixed training budget.
def exercise_4():
    raise NotImplementedError("Evaluate untouched inputs")


# Exercise 5: Separate training from inference
# Run forward twice with the trained parameters and the same inputs.
def exercise_5():
    raise NotImplementedError("Separate training from inference")


# Exercise 6: Check an architecture change
# Explain and verify how adding one hidden coordinate changes the parameter count for this layout.
def exercise_6():
    raise NotImplementedError("Check an architecture change")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
