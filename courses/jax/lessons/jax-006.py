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


# Exercise 1: Inspect the leaf ledger
# Map each parameter leaf to its shape.
def exercise_1():
    raise NotImplementedError("Inspect the leaf ledger")


# Exercise 2: Count stored scalars
# Count the parameter entries across all leaves.
def exercise_2():
    raise NotImplementedError("Count stored scalars")


# Exercise 3: Reconstruct the tree
# Flatten params, retain the structure, then unflatten.
def exercise_3():
    raise NotImplementedError("Reconstruct the tree")


# Exercise 4: Reject a missing field
# Try updating with a tree that lacks the bias.
def exercise_4():
    raise NotImplementedError("Reject a missing field")


# Exercise 5: Apply distinct gradients
# Use matrix gradient 2 and bias gradient [3,-4] at rate 0.5.
def exercise_5():
    raise NotImplementedError("Apply distinct gradients")


# Exercise 6: Transfer to nested state
# Map zeros_like over a tuple containing params and a scalar counter array.
def exercise_6():
    raise NotImplementedError("Transfer to nested state")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
