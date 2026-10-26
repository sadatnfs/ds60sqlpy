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


# Exercise 1: Replay a transition
# Apply observation 5 twice, independently, to the same empty state.
def exercise_1():
    raise NotImplementedError("Replay a transition")


# Exercise 2: Accumulate a sequence
# Process observations [1,3,8] in order using returned state.
def exercise_2():
    raise NotImplementedError("Accumulate a sequence")


# Exercise 3: Refuse an empty mean
# Request the mean of the empty state.
def exercise_3():
    raise NotImplementedError("Refuse an empty mean")


# Exercise 4: Extend a saved state
# Continue from total 12/count 3 with observation 20.
def exercise_4():
    raise NotImplementedError("Extend a saved state")


# Exercise 5: Check order-independent totals
# Accumulate [8,3,1] and compare with the same values in ascending order.
def exercise_5():
    raise NotImplementedError("Check order-independent totals")


# Exercise 6: Merge states
# Merge totals/counts (6,2), (9,3), (5,1) and explain the sufficient information.
def exercise_6():
    raise NotImplementedError("Merge states")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
