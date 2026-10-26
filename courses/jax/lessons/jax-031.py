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


# Exercise 1: Audit the initial gradient
# Compare autodiff with the explicit matrix gradient at zero.
def exercise_1():
    raise NotImplementedError("Audit the initial gradient")


# Exercise 2: Check an independent optimum
# Solve the full quadratic least-squares problem directly.
def exercise_2():
    raise NotImplementedError("Check an independent optimum")


# Exercise 3: Replay the fixed budget
# Train again from zero with identical configuration.
def exercise_3():
    raise NotImplementedError("Replay the fixed budget")


# Exercise 4: Resume a partial trajectory
# Compare 400 consecutive steps with 200 followed by 200 from the returned coefficients.
def exercise_4():
    raise NotImplementedError("Resume a partial trajectory")


# Exercise 5: Verify the held-out split
# Check that the four held-out inputs do not coincide with training inputs.
def exercise_5():
    raise NotImplementedError("Verify the held-out split")


# Exercise 6: Transfer the coefficient rule
# Predict at x=3 using the known coefficients and distinguish extrapolation from the held-out interpolation study.
def exercise_6():
    raise NotImplementedError("Transfer the coefficient rule")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
