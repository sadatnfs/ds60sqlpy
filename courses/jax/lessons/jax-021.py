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


# Exercise 1: Reuse draws in a derivative check
# Central-difference the mean parameter with the same noise array for both perturbations.
def exercise_1():
    raise NotImplementedError("Reuse draws in a derivative check")


# Exercise 2: Parameterize a positive scale
# Use scale=exp(log_scale) and differentiate at log(3) with the control pair.
def exercise_2():
    raise NotImplementedError("Parameterize a positive scale")


# Exercise 3: Check a zero-mean population formula
# Evaluate the control pair with mean zero and scale two.
def exercise_3():
    raise NotImplementedError("Check a zero-mean population formula")


# Exercise 4: Retain the Monte Carlo count
# Calculate an estimated standard error for the mean squared transformed draws using sample variance.
def exercise_4():
    raise NotImplementedError("Retain the Monte Carlo count")


# Exercise 5: Vectorize parameter comparisons
# Evaluate means [0,1,2] at scale three with the same control pair.
def exercise_5():
    raise NotImplementedError("Vectorize parameter comparisons")


# Exercise 6: Replay the sampled input
# Recreate noise with the same root key, shape and dtype.
def exercise_6():
    raise NotImplementedError("Replay the sampled input")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
