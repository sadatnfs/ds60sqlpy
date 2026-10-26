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


# Exercise 1: Check the first derivative
# Calculate grad at [1,2] before inspecting curvature.
def exercise_1():
    raise NotImplementedError("Check the first derivative")


# Exercise 2: Reverse the transform order
# Compare jacrev of grad with jacfwd of grad.
def exercise_2():
    raise NotImplementedError("Reverse the transform order")


# Exercise 3: Check a matrix-free product numerically
# Central-difference the gradient along [2,-1] with h=1e-5.
def exercise_3():
    raise NotImplementedError("Check a matrix-free product numerically")


# Exercise 4: Interpret directional curvature
# Calculate v dot H v for v=[2,-1].
def exercise_4():
    raise NotImplementedError("Interpret directional curvature")


# Exercise 5: Change the evaluation point
# Evaluate the quadratic's Hessian at [-3,7].
def exercise_5():
    raise NotImplementedError("Change the evaluation point")


# Exercise 6: Contrast nonlinear curvature
# Evaluate the second derivative of x^4 at x=0 and x=2.
def exercise_6():
    raise NotImplementedError("Contrast nonlinear curvature")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
