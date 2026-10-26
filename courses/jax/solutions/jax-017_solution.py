"""Small offline JAX mechanism investigation; CPU evidence only."""

from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp

import tempfile
from pathlib import Path

# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)


def next_state(state):
    weight, velocity, key, count = state
    next_key, draw_key = jax.random.split(key)
    noise = jax.random.normal(draw_key, (), dtype=jnp.float64)
    gradient = 2.0 * (weight - 2.0) + 0.01 * noise
    velocity = 0.9 * velocity + gradient
    return weight - 0.1 * velocity, velocity, next_key, count + 1


def prepared_state():
    state = (
        jnp.float64(0.0),
        jnp.float64(0.0),
        jax.random.key(52, impl="threefry2x32"),
        jnp.int64(0),
    )
    return next_state(next_state(state))


def save_state(path, state):
    w, v, key, count = state
    np.savez(
        path,
        weight=np.asarray(w),
        velocity=np.asarray(v),
        key=np.asarray(jax.random.key_data(key)),
        count=np.asarray(count),
    )


def load_state(path):
    with np.load(path, allow_pickle=False) as saved:
        return (
            jnp.asarray(saved["weight"]),
            jnp.asarray(saved["velocity"]),
            jax.random.wrap_key_data(jnp.asarray(saved["key"]), impl="threefry2x32"),
            jnp.asarray(saved["count"]),
        )


def compare(left, right):
    close(left[0], right[0])
    close(left[1], right[1])
    assert np.array_equal(
        np.asarray(jax.random.key_data(left[2])), np.asarray(jax.random.key_data(right[2]))
    )
    assert int(left[3]) == int(right[3])


def main():
    # Case 1: Reconstruct the next transition
    state = prepared_state()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.npz"
        save_state(path, state)
        restored = load_state(path)
        compare(next_state(state), next_state(restored))
        assert int(next_state(restored)[3]) == 3

    # Case 2: Omit history deliberately
    state = prepared_state()
    wrong = (state[0], jnp.float64(0.0), state[2], state[3])
    assert not np.isclose(float(next_state(state)[0]), float(next_state(wrong)[0]))

    # Case 3: Check a nontrivial checkpoint
    state = prepared_state()
    assert int(state[3]) == 2
    assert float(state[1]) != 0.0

    # Case 4: Replay from the same root
    compare(prepared_state(), prepared_state())

    # Case 5: Validate serialization values
    state = prepared_state()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.npz"
        save_state(path, state)
        restored = load_state(path)
        compare(state, restored)
        assert restored[0].shape == () and restored[0].dtype == jnp.float64

    # Case 6: Show random-state importance
    state = prepared_state()
    other = (state[0], state[1], jax.random.key(999, impl="threefry2x32"), state[3])
    a, b = next_state(state), next_state(other)
    assert not np.array_equal(
        np.asarray(jax.random.key_data(a[2])), np.asarray(jax.random.key_data(b[2]))
    )

    # Case 7: Check owned cleanup
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.npz"
        save_state(path, prepared_state())
        assert path.is_file()
    assert not path.exists()

    # Case 8: Continue twice
    state = prepared_state()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.npz"
        save_state(path, state)
        restored = load_state(path)
        left, right = next_state(next_state(state)), next_state(next_state(restored))
        compare(left, right)
        assert int(right[3]) == 4

    print("jax-017" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
