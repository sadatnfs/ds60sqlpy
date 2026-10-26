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


def draw_step(key):
    next_key, sample_key = jax.random.split(key)
    return next_key, jax.random.normal(sample_key, shape=(4,), dtype=jnp.float64)


def same_key(left, right):
    return np.array_equal(
        np.asarray(jax.random.key_data(left)), np.asarray(jax.random.key_data(right))
    )


def main():
    # Case 1: Reuse reproduces
    key = jax.random.key(7)
    a = jax.random.normal(key, (4,))
    b = jax.random.normal(key, (4,))
    assert np.array_equal(np.asarray(a), np.asarray(b))

    # Case 2: Return the next key
    key = jax.random.key(7)
    next_key, first = draw_step(key)
    last_key, second = draw_step(next_key)
    assert not same_key(key, next_key)
    assert not same_key(next_key, last_key)
    close(draw_step(key)[1], first)

    # Case 3: Inspect a typed key
    key = jax.random.key(11)
    assert key.shape == ()
    assert np.issubdtype(np.asarray(jax.random.key_data(key)).dtype, np.integer)

    # Case 4: Split four streams
    keys = jax.random.split(jax.random.key(11), 4)
    assert keys.shape == (4,)
    assert len({np.asarray(jax.random.key_data(k)).tobytes() for k in keys}) == 4

    # Case 5: Replay a record identity
    root = jax.random.key(3)
    a = jax.random.fold_in(root, 42)
    b = jax.random.fold_in(root, 42)
    assert same_key(a, b)
    close(jax.random.uniform(a, (3,)), jax.random.uniform(b, (3,)))

    # Case 6: Separate identities
    root = jax.random.key(3)
    assert not same_key(jax.random.fold_in(root, 42), jax.random.fold_in(root, 43))

    # Case 7: Replay a whole transition
    def sequence():
        key = jax.random.key(19)
        values = []
        for _ in range(3):
            key, value = draw_step(key)
            values.append(value)
        return key, jnp.stack(values)

    a, x = sequence()
    b, y = sequence()
    assert same_key(a, b)
    close(x, y)

    # Case 8: Diagnose repeated example masks
    key = jax.random.key(5)
    a = jax.random.bernoulli(key, 0.5, (8,))
    b = jax.random.bernoulli(key, 0.5, (8,))
    assert np.array_equal(np.asarray(a), np.asarray(b))
    k1, k2 = jax.random.split(key)
    assert not same_key(k1, k2)

    print("jax-005" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
