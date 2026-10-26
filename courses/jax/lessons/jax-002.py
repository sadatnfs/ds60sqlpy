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


# Exercise 1: Center each observation
# Subtract each row's mean while preserving a singleton feature axis.
def exercise_1():
    raise NotImplementedError("Center each observation")


# Exercise 2: Broadcast feature offsets
# Add [10,20,30] to each observation.
def exercise_2():
    raise NotImplementedError("Broadcast feature offsets")


# Exercise 3: Broadcast observation offsets
# Add 10 to row zero and 20 to row one.
def exercise_3():
    raise NotImplementedError("Broadcast observation offsets")


# Exercise 4: Accumulate an update
# Add five at index zero using .at and retain the original vector.
def exercise_4():
    raise NotImplementedError("Accumulate an update")


# Exercise 5: Enforce the index boundary
# Try replacing index three in a three-element vector.
def exercise_5():
    raise NotImplementedError("Enforce the index boundary")


# Exercise 6: Transfer the axis rule
# Row-center a 3-by-2 table and assert each row sum, without hard-coding row count.
def exercise_6():
    raise NotImplementedError("Transfer the axis rule")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
