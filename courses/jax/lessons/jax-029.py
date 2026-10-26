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


# Exercise 1: Perturb only the future
# Change the final value row and compare the first two attention outputs.
def exercise_1():
    raise NotImplementedError("Perturb only the future")


# Exercise 2: Test the scale with nonuniform scores
# Use one query [1,0], keys [[1,0],[0,1]] and values [[2,0],[0,2]].
def exercise_2():
    raise NotImplementedError("Test the scale with nonuniform scores")


# Exercise 3: Refuse an empty allowed set
# Remove every key from the first query's mask.
def exercise_3():
    raise NotImplementedError("Refuse an empty allowed set")


# Exercise 4: Trace value gradients
# Differentiate the sum of all attention outputs with respect to V in the zero-score fixture.
def exercise_4():
    raise NotImplementedError("Trace value gradients")


# Exercise 5: Count and bound the adapter
# Count the trainable factor entries and verify the product's maximum rank.
def exercise_5():
    raise NotImplementedError("Count and bound the adapter")


# Exercise 6: Compile the admitted operation
# JIT the pure attention helper and compare the exact fixture.
def exercise_6():
    raise NotImplementedError("Compile the admitted operation")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
