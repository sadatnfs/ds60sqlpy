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


# Exercise 1: Inspect mesh identity
# Check the named mesh size and its actual devices.
def exercise_1():
    raise NotImplementedError("Inspect mesh identity")


# Exercise 2: Round-trip values
# Place the table and convert it back to a host array.
def exercise_2():
    raise NotImplementedError("Round-trip values")


# Exercise 3: Inspect the specification
# Compare the row-layout specification with an empty replicated specification.
def exercise_3():
    raise NotImplementedError("Inspect the specification")


# Exercise 4: Differentiate a placed calculation
# Differentiate the sum of squares for the placed input.
def exercise_4():
    raise NotImplementedError("Differentiate a placed calculation")


# Exercise 5: Change the row count
# Place a 5-by-2 table under the same named row layout.
def exercise_5():
    raise NotImplementedError("Change the row count")


# Exercise 6: State the evidence limit
# Inspect how many physical devices actually hold the result.
def exercise_6():
    raise NotImplementedError("State the evidence limit")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
