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


# Exercise 1: Probe the first input coordinate
# Use direction [1,0] in a JVP.
def exercise_1():
    raise NotImplementedError("Probe the first input coordinate")


# Exercise 2: Probe the second output coordinate
# Use output cotangent [0,1,0] in the pullback.
def exercise_2():
    raise NotImplementedError("Probe the second output coordinate")


# Exercise 3: Check duality
# Compare u dot Jv with v dot the pullback of u for the stated vectors.
def exercise_3():
    raise NotImplementedError("Check duality")


# Exercise 4: Check a directional finite difference
# Perturb point along [3,4] using h=1e-5.
def exercise_4():
    raise NotImplementedError("Check a directional finite difference")


# Exercise 5: Change the point
# Evaluate the Jacobian at [1,1] with jacfwd.
def exercise_5():
    raise NotImplementedError("Change the point")


# Exercise 6: Recover a scalar gradient
# Differentiate the weighted output sum with weights [1,2,3].
def exercise_6():
    raise NotImplementedError("Recover a scalar gradient")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
