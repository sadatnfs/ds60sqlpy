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


# Exercise 1: Differentiate the initial carry
# Differentiate the final scan output with respect to initial state.
def exercise_1():
    raise NotImplementedError("Differentiate the initial carry")


# Exercise 2: Differentiate sequence inputs
# Differentiate the final output with respect to the three input values.
def exercise_2():
    raise NotImplementedError("Differentiate sequence inputs")


# Exercise 3: Handle an empty scan
# Run the recurrence on an empty input vector with initial state five.
def exercise_3():
    raise NotImplementedError("Handle an empty scan")


# Exercise 4: Use a fixed-index loop
# Accumulate the first four nonnegative integers with fori_loop.
def exercise_4():
    raise NotImplementedError("Use a fixed-index loop")


# Exercise 5: Inspect a dynamic stopping rule
# Double a positive scalar until it is at least ten; calculate its local JVP at one.
def exercise_5():
    raise NotImplementedError("Inspect a dynamic stopping rule")


# Exercise 6: Transfer to a batched state
# Run the same recurrence with a two-coordinate carry and two input rows.
def exercise_6():
    raise NotImplementedError("Transfer to a batched state")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
