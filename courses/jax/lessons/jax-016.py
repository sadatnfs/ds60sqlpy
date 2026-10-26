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


# Exercise 1: Replay a mask
# Use the same key twice in training mode.
def exercise_1():
    raise NotImplementedError("Replay a mask")


# Exercise 2: Keep every activation
# Use keep probability one in training mode.
def exercise_2():
    raise NotImplementedError("Keep every activation")


# Exercise 3: Reject zero keep probability
# Validate q=0 before the transform.
def exercise_3():
    raise NotImplementedError("Reject zero keep probability")


# Exercise 4: Differentiate with a fixed mask
# Differentiate the sum of dropped activations with respect to the input.
def exercise_4():
    raise NotImplementedError("Differentiate with a fixed mask")


# Exercise 5: Compile the mode policy
# JIT the helper with training and keep static, then test evaluation.
def exercise_5():
    raise NotImplementedError("Compile the mode policy")


# Exercise 6: Inspect a larger sample without a universal claim
# Drop a length-4096 vector of ones with the pinned key and report its mean.
def exercise_6():
    raise NotImplementedError("Inspect a larger sample without a universal claim")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
