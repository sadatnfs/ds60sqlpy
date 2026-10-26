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


# Exercise 1: Change the derivative input
# Check the rematerialized cubic gradient at [-2,0,2].
def exercise_1():
    raise NotImplementedError("Change the derivative input")


# Exercise 2: Compose checkpointing with JIT
# JIT the gradient of the rematerialized function.
def exercise_2():
    raise NotImplementedError("Compose checkpointing with JIT")


# Exercise 3: Continue from returned ownership
# Apply the donated increment transition twice, each time retaining the returned array.
def exercise_3():
    raise NotImplementedError("Continue from returned ownership")


# Exercise 4: Keep an ordinary baseline
# Compare a donated update against a non-donating implementation using independently created inputs.
def exercise_4():
    raise NotImplementedError("Keep an ordinary baseline")


# Exercise 5: Check a higher derivative
# Calculate the Hessian diagonal of the rematerialized cubic at [1,2].
def exercise_5():
    raise NotImplementedError("Check a higher derivative")


# Exercise 6: Separate a resource claim
# Inspect result size for a donated length-four update and state what it does not measure.
def exercise_6():
    raise NotImplementedError("Separate a resource claim")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
