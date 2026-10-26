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


def add_then_subtract(big, increment):
    intermediate = big + increment
    return intermediate - big


def main():
    # Case 1: An increment disappears
    close(add_then_subtract(jnp.float32(1e8), jnp.float32(1.0)), 0.0)
    close(add_then_subtract(jnp.float64(1e8), jnp.float64(1.0)), 1.0)

    # Case 2: A finite stable objective
    value = jnp.logaddexp(jnp.float64(0.0), jnp.float64(1000.0))
    assert bool(jnp.isfinite(value))
    close(value, 1000.0)

    # Case 3: Inspect precision
    assert jnp.array([1.0], dtype=jnp.float32).dtype == jnp.float32
    assert jnp.array([1.0], dtype=jnp.float64).dtype == jnp.float64

    # Case 4: Calculate epsilon
    assert float(jnp.finfo(jnp.float32).eps) == 2.0**-23
    assert float(jnp.finfo(jnp.float64).eps) == 2.0**-52

    # Case 5: Use an absolute bound
    close(jnp.float64(1e-12), 0.0, atol=2e-12, rtol=0.0)

    # Case 6: Keep counts exact
    counts = jnp.array([2, 3, 5], dtype=jnp.int32)
    assert counts.sum().shape == ()
    assert int(counts.sum()) == 10

    # Case 7: Shift scores safely
    scores = jnp.array([0.0, math.log(3.0)])
    a = jax.scipy.special.logsumexp(scores)
    b = jax.scipy.special.logsumexp(scores + 1000.0)
    close(a, math.log(4.0))
    close(b - a, 1000.0)

    # Case 8: Recognize invalid data
    assert not bool(jnp.isfinite(jnp.array([jnp.nan, jnp.inf])).all())

    print("jax-003" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
