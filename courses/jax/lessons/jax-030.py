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


# Exercise 1: Check a penalty convention
# Solve with penalty 0.1 and verify the gradient of that same penalized objective.
def exercise_1():
    raise NotImplementedError("Check a penalty convention")


# Exercise 2: Preserve row identity under permutation
# Reverse design, targets and mask together.
def exercise_2():
    raise NotImplementedError("Preserve row identity under permutation")


# Exercise 3: Reject an empty population
# Admit a completely false mask.
def exercise_3():
    raise NotImplementedError("Reject an empty population")


# Exercise 4: Reject an invalid penalty
# Admit a negative ridge penalty.
def exercise_4():
    raise NotImplementedError("Reject an invalid penalty")


# Exercise 5: Check transformation parity
# Compile the solve on admitted inputs and compare with the eager result.
def exercise_5():
    raise NotImplementedError("Check transformation parity")


# Exercise 6: Transfer the target rule
# Use targets [2,5,8] with the same feature rows.
def exercise_6():
    raise NotImplementedError("Transfer the target rule")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
