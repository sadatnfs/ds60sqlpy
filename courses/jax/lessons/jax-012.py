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


# Exercise 1: Compare with a literal loop
# Evaluate the shared predictor by a Python list of calls and by vmap.
def exercise_1():
    raise NotImplementedError("Compare with a literal loop")


# Exercise 2: Reduce gradients deliberately
# Compare the mean per-example gradient with grad of the mean loss.
def exercise_2():
    raise NotImplementedError("Reduce gradients deliberately")


# Exercise 3: Change to a sum
# Differentiate the summed batch loss.
def exercise_3():
    raise NotImplementedError("Change to a sum")


# Exercise 4: Map several models
# Apply weights [[1,0],[0,1],[1,1]] separately to feature [2,3].
def exercise_4():
    raise NotImplementedError("Map several models")


# Exercise 5: Compose with JIT
# JIT the vectorized predictor and compare the values.
def exercise_5():
    raise NotImplementedError("Compose with JIT")


# Exercise 6: Allocate random streams per row
# Split one root into three keys and map a fixed-shape normal draw over them.
def exercise_6():
    raise NotImplementedError("Allocate random streams per row")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
