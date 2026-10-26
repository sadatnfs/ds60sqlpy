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


# Exercise 1: Compare eager and compiled values
# Evaluate a smooth polynomial eagerly and under JIT on [1,2,3].
def exercise_1():
    raise NotImplementedError("Compare eager and compiled values")


# Exercise 2: Observe a shape specialization
# Call one fresh traced function with length two and length three.
def exercise_2():
    raise NotImplementedError("Observe a shape specialization")


# Exercise 3: Expose a traced Boolean error
# JIT a Python if that depends on the numerical value of an array scalar.
def exercise_3():
    raise NotImplementedError("Expose a traced Boolean error")


# Exercise 4: Keep zero iterations defined
# Evaluate the static loop with n=0.
def exercise_4():
    raise NotImplementedError("Keep zero iterations defined")


# Exercise 5: Compose differentiation with compilation
# Differentiate the compiled square-sum function at [1,2].
def exercise_5():
    raise NotImplementedError("Compose differentiation with compilation")


# Exercise 6: Inspect the staged operations
# Create a jaxpr for x*x+1 and identify numerical equations.
def exercise_6():
    raise NotImplementedError("Inspect the staged operations")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
