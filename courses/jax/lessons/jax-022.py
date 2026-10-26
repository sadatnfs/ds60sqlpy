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


# Exercise 1: Compare an ordinary gradient
# Compare the custom softplus gradient with sigmoid at [-2,0,2].
def exercise_1():
    raise NotImplementedError("Compare an ordinary gradient")


# Exercise 2: Check tangent linearity
# Compare JVP tangents two, three and five at x=1.
def exercise_2():
    raise NotImplementedError("Check tangent linearity")


# Exercise 3: Check an extreme stable input
# Evaluate softplus and its gradient at 1000.
def exercise_3():
    raise NotImplementedError("Check an extreme stable input")


# Exercise 4: Differentiate a composition
# Differentiate four times custom_square at three.
def exercise_4():
    raise NotImplementedError("Differentiate a composition")


# Exercise 5: Check a second derivative
# Differentiate the custom softplus gradient at zero.
def exercise_5():
    raise NotImplementedError("Check a second derivative")


# Exercise 6: Name the forward-mode limit
# Attempt a direct JVP through the custom_vjp square.
def exercise_6():
    raise NotImplementedError("Name the forward-mode limit")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
