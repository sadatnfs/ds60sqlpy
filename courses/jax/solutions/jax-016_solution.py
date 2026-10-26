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


def validate_keep(keep):
    if not math.isfinite(keep) or not 0.0 < keep <= 1.0:
        raise ValueError("keep probability must be in (0,1]")


def dropout(values, key, *, training, keep=0.5):
    if not training:
        return values
    mask = jax.random.bernoulli(key, keep, values.shape)
    return jnp.where(mask, values / keep, 0.0)


values = jnp.ones(16)
key = jax.random.key(41)


def main():
    # Case 1: Inspect a training mask
    validate_keep(0.5)
    result = dropout(values, key, training=True, keep=0.5)
    assert bool(jnp.all((result == 0.0) | (result == 2.0)))

    # Case 2: Evaluation is explicit
    close(dropout(values, key, training=False), values)
    close(dropout(values, jax.random.key(99), training=False), values)

    # Case 3: Replay a mask
    a = dropout(values, key, training=True)
    b = dropout(values, key, training=True)
    close(a, b)

    # Case 4: Keep every activation
    validate_keep(1.0)
    close(dropout(values, key, training=True, keep=1.0), values)

    # Case 5: Reject zero keep probability
    try:
        validate_keep(0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero keep accepted")

    # Case 6: Differentiate with a fixed mask
    g = jax.grad(lambda x: dropout(x, key, training=True).sum())(values)
    close(g, dropout(values, key, training=True))

    # Case 7: Compile the mode policy
    compiled = jax.jit(dropout, static_argnames=("training", "keep"))
    close(compiled(values, key, training=False, keep=0.5), values)

    # Case 8: Inspect a larger sample without a universal claim
    result = dropout(jnp.ones(4096), key, training=True)
    mean = float(result.mean())
    assert 0.0 <= mean <= 2.0
    assert bool(jnp.all((result == 0.0) | (result == 2.0)))

    print("jax-016" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
