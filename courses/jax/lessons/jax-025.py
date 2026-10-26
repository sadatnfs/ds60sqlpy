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


# Exercise 1: Reject an empty timing sample
# Request zero repetitions.
def exercise_1():
    raise NotImplementedError("Reject an empty timing sample")


# Exercise 2: Retain the shape contract
# Inspect the result shape of a completed product.
def exercise_2():
    raise NotImplementedError("Retain the shape contract")


# Exercise 3: Compare eager and compiled outputs
# Compute the same product through eager and jitted functions.
def exercise_3():
    raise NotImplementedError("Compare eager and compiled outputs")


# Exercise 4: Report a declared summary
# Collect three completed times and calculate the median.
def exercise_4():
    raise NotImplementedError("Report a declared summary")


# Exercise 5: Change workload size explicitly
# Evaluate the product for an 8-by-8 array and check it against NumPy.
def exercise_5():
    raise NotImplementedError("Change workload size explicitly")


# Exercise 6: Identify the executed backend
# Record the backend and result-device platform for this CPU lesson.
def exercise_6():
    raise NotImplementedError("Identify the executed backend")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
