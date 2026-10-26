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


# Exercise 1: Check another smooth point
# Evaluate the gradient at weight one using the closed form.
def exercise_1():
    raise NotImplementedError("Check another smooth point")


# Exercise 2: Use a central difference
# Estimate the derivative at w=0.7 with h=1e-5 and compare to autodiff.
def exercise_2():
    raise NotImplementedError("Use a central difference")


# Exercise 3: Change the reduction
# Differentiate the summed squared error at zero.
def exercise_3():
    raise NotImplementedError("Change the reduction")


# Exercise 4: Inspect the optimum
# Evaluate value and derivative at w=2.
def exercise_4():
    raise NotImplementedError("Inspect the optimum")


# Exercise 5: Differentiate a parameter tree
# Differentiate mean squared error for a weight and bias, both initially zero.
def exercise_5():
    raise NotImplementedError("Differentiate a parameter tree")


# Exercise 6: Choose a scalar objective
# Demonstrate that grad refuses an unreduced vector loss, then reduce it explicitly.
def exercise_6():
    raise NotImplementedError("Choose a scalar objective")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
