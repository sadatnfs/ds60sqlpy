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


# Exercise 1: Change the right-hand side
# Solve the same matrix for b=[4,3].
def exercise_1():
    raise NotImplementedError("Change the right-hand side")


# Exercise 2: Differentiate with respect to b
# Differentiate the sum of solved coordinates with respect to the right-hand side.
def exercise_2():
    raise NotImplementedError("Differentiate with respect to b")


# Exercise 3: Reject a singular fixture
# Apply the declared admission policy to [[1,2],[2,4]].
def exercise_3():
    raise NotImplementedError("Reject a singular fixture")


# Exercise 4: Check the sensitivity numerically
# Central-difference the summed parameterized solution at zero with h=1e-5.
def exercise_4():
    raise NotImplementedError("Check the sensitivity numerically")


# Exercise 5: Interpret ridge regularization
# Fit y=2x on x=[1,2,3] with penalty lambda=14 and no intercept.
def exercise_5():
    raise NotImplementedError("Interpret ridge regularization")


# Exercise 6: Compile a valid solve
# JIT the solution calculation and compare its residual.
def exercise_6():
    raise NotImplementedError("Compile a valid solve")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
