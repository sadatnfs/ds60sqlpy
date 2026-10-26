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


# Exercise 1: Pull back to the right-hand side
# Differentiate the summed solution with respect to b.
def exercise_1():
    raise NotImplementedError("Pull back to the right-hand side")


# Exercise 2: Change the diagonal
# Set theta two and solve the same right-hand side.
def exercise_2():
    raise NotImplementedError("Change the diagonal")


# Exercise 3: Compare an ordinary solve
# Compare with jnp.linalg.solve for theta 0.5.
def exercise_3():
    raise NotImplementedError("Compare an ordinary solve")


# Exercise 4: Detect a bogus solver
# Supply a solver returning zeros and test its residual.
def exercise_4():
    raise NotImplementedError("Detect a bogus solver")


# Exercise 5: Check a second derivative
# Differentiate the summed solution twice at theta zero.
def exercise_5():
    raise NotImplementedError("Check a second derivative")


# Exercise 6: Compile the valid interface
# JIT the implicit solution and compare the residual at theta one.
def exercise_6():
    raise NotImplementedError("Compile the valid interface")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
