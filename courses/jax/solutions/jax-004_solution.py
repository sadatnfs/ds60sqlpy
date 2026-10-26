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


def transition(state, value):
    total, count = state
    return total + value, count + 1


def mean_of(state):
    total, count = state
    if int(count) <= 0:
        raise ValueError("no observations")
    return total / count


initial = (jnp.float64(0.0), jnp.int64(0))


def main():
    # Case 1: Retain old and new state
    new = transition(initial, 3.0)
    close(initial[0], 0.0)
    assert int(initial[1]) == 0
    close(mean_of(new), 3.0)

    # Case 2: Counts change weighting
    combined = (jnp.float64(4.0 + 10.0), jnp.int64(2 + 1))
    close(mean_of(combined), 14 / 3)
    assert not np.isclose(float(mean_of(combined)), 6.0)

    # Case 3: Replay a transition
    left = transition(initial, 5.0)
    right = transition(initial, 5.0)
    close(left[0], right[0])
    assert int(left[1]) == int(right[1]) == 1

    # Case 4: Accumulate a sequence
    state = initial
    for value in [1.0, 3.0, 8.0]:
        state = transition(state, value)
    close(state[0], 12.0)
    assert int(state[1]) == 3
    close(mean_of(state), 4.0)

    # Case 5: Refuse an empty mean
    try:
        mean_of(initial)
    except ValueError:
        pass
    else:
        raise AssertionError("empty mean accepted")

    # Case 6: Extend a saved state
    state = transition((jnp.float64(12.0), jnp.int64(3)), 20.0)
    close(mean_of(state), 8.0)

    # Case 7: Check order-independent totals
    state = initial
    for value in [8.0, 3.0, 1.0]:
        state = transition(state, value)
    close(state[0], 12.0)
    assert int(state[1]) == 3

    # Case 8: Merge states
    groups = [(6.0, 2), (9.0, 3), (5.0, 1)]
    close(sum(a for a, n in groups) / sum(n for a, n in groups), 10 / 3)

    print("jax-004" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
