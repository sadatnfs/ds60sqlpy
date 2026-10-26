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


# Exercise 1: Change only the abstract row count
# Infer gram's output for a (7,2) input.
def exercise_1():
    raise NotImplementedError("Change only the abstract row count")


# Exercise 2: Change the feature count
# Infer gram's output for a (3,4) input.
def exercise_2():
    raise NotImplementedError("Change the feature count")


# Exercise 3: Inspect staged dependencies
# Create a jaxpr for gram and inspect its output count.
def exercise_3():
    raise NotImplementedError("Inspect staged dependencies")


# Exercise 4: Execute another compatible value
# Reuse the compiled signature on twice the original input.
def exercise_4():
    raise NotImplementedError("Execute another compatible value")


# Exercise 5: Compose a scalar sensitivity
# Differentiate the sum of the Gram matrix with respect to input values.
def exercise_5():
    raise NotImplementedError("Compose a scalar sensitivity")


# Exercise 6: Separate metadata from values
# Use a zero input with the same abstract signature and compare the output shape and values.
def exercise_6():
    raise NotImplementedError("Separate metadata from values")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
