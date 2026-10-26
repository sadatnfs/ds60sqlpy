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


# Exercise 1: Trace plain SGD
# Update w=1 with gradient three and rate 0.2.
def exercise_1():
    raise NotImplementedError("Trace plain SGD")


# Exercise 2: Continue momentum
# Apply gradient two twice from weight and velocity zero.
def exercise_2():
    raise NotImplementedError("Continue momentum")


# Exercise 3: Continue Adam's counter
# Apply the same gradient twice while retaining Adam state.
def exercise_3():
    raise NotImplementedError("Continue Adam's counter")


# Exercise 4: Preserve zero-gradient history
# After one positive gradient, apply a zero gradient with retained Adam state.
def exercise_4():
    raise NotImplementedError("Preserve zero-gradient history")


# Exercise 5: Compile the transition
# JIT adam_step and compare its first update with eager execution.
def exercise_5():
    raise NotImplementedError("Compile the transition")


# Exercise 6: Reverse the gradient
# Apply gradient minus two from zero state.
def exercise_6():
    raise NotImplementedError("Reverse the gradient")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
