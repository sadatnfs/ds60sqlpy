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


table = jnp.arange(6.0, dtype=jnp.float64).reshape(2, 3)


def replace_at(values, index, value):
    if type(index) is not int or not 0 <= index < values.shape[0]:
        raise ValueError("index outside the vector")
    return values.at[index].set(value)


def main():
    # Case 1: Two valid reductions
    close(table.sum(axis=1), [3.0, 12.0])
    close(table.sum(axis=0), [3.0, 5.0, 7.0])

    # Case 2: Return a changed value
    old = jnp.array([10.0, 20.0, 30.0])
    new = replace_at(old, 1, 99.0)
    close(new, [10.0, 99.0, 30.0])
    close(old, [10.0, 20.0, 30.0])

    # Case 3: Center each observation
    centered = table - table.mean(axis=1, keepdims=True)
    close(centered, [[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]])
    close(centered.sum(axis=1), [0.0, 0.0])

    # Case 4: Broadcast feature offsets
    close(table + jnp.array([10.0, 20.0, 30.0]), [[10.0, 21.0, 32.0], [13.0, 24.0, 35.0]])

    # Case 5: Broadcast observation offsets
    close(table + jnp.array([10.0, 20.0])[:, None], [[10.0, 11.0, 12.0], [23.0, 24.0, 25.0]])

    # Case 6: Accumulate an update
    old = jnp.array([1.0, 2.0])
    close(old.at[0].add(5.0), [6.0, 2.0])
    close(old, [1.0, 2.0])

    # Case 7: Enforce the index boundary
    try:
        replace_at(jnp.zeros(3), 3, 1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("bad index accepted")

    # Case 8: Transfer the axis rule
    other = jnp.arange(6.0).reshape(3, 2)
    centered = other - other.mean(axis=1, keepdims=True)
    assert centered.shape == (3, 2)
    close(centered.sum(axis=1), jnp.zeros(3))

    print("jax-002" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
