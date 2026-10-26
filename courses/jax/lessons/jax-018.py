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


# Exercise 1: Expose a host conversion
# Attempt np.asarray on an argument inside JIT.
def exercise_1():
    raise NotImplementedError("Expose a host conversion")


# Exercise 2: Expose a dynamic output length
# JIT x[x>0] on a mixed-sign vector.
def exercise_2():
    raise NotImplementedError("Expose a dynamic output length")


# Exercise 3: Use a fixed-shape alternative
# Sum positive values using where and a fixed-shaped vector.
def exercise_3():
    raise NotImplementedError("Use a fixed-shape alternative")


# Exercise 4: Print a runtime diagnostic
# Emit a bounded sum through debug.print inside a jitted function.
def exercise_4():
    raise NotImplementedError("Print a runtime diagnostic")


# Exercise 5: Compare with JIT disabled
# Evaluate the same jitted polynomial within and outside disable_jit.
def exercise_5():
    raise NotImplementedError("Compare with JIT disabled")


# Exercise 6: Retain the positive-domain derivative
# Differentiate the safe extension at positive values [1,2,4].
def exercise_6():
    raise NotImplementedError("Retain the positive-domain derivative")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
