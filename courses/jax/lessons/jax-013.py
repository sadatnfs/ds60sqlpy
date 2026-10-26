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


# Exercise 1: Append ignored storage
# Append two ignored rows and show that the objective stays the same.
def exercise_1():
    raise NotImplementedError("Append ignored storage")


# Exercise 2: Reject an empty objective
# Admit a mask with no active targets.
def exercise_2():
    raise NotImplementedError("Reject an empty objective")


# Exercise 3: Check target identity
# Use logits [log(3),0] and compare targets zero and one.
def exercise_3():
    raise NotImplementedError("Check target identity")


# Exercise 4: Keep an extreme logit finite
# Score target zero for logits [1000,0,-1000].
def exercise_4():
    raise NotImplementedError("Keep an extreme logit finite")


# Exercise 5: Reject an active sentinel
# Mark the -100 target active and apply admission.
def exercise_5():
    raise NotImplementedError("Reject an active sentinel")


# Exercise 6: Compile the admitted calculation
# JIT token_mean on the admitted fixture and compare with the eager objective.
def exercise_6():
    raise NotImplementedError("Compile the admitted calculation")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
