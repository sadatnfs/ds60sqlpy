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


# Exercise 1: Inspect a typed key
# Create a key and inspect its scalar shape and key-data representation.
def exercise_1():
    raise NotImplementedError("Inspect a typed key")


# Exercise 2: Split four streams
# Split one key into four and verify pairwise different key data.
def exercise_2():
    raise NotImplementedError("Split four streams")


# Exercise 3: Replay a record identity
# Fold record ID 42 into the same root twice.
def exercise_3():
    raise NotImplementedError("Replay a record identity")


# Exercise 4: Separate identities
# Fold IDs 42 and 43 into one root and compare key data.
def exercise_4():
    raise NotImplementedError("Separate identities")


# Exercise 5: Replay a whole transition
# Run three draw_step transitions twice from root key 19.
def exercise_5():
    raise NotImplementedError("Replay a whole transition")


# Exercise 6: Diagnose repeated example masks
# Call Bernoulli twice with one key and compare it with an explicit split policy.
def exercise_6():
    raise NotImplementedError("Diagnose repeated example masks")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
