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


def momentum_step(weight, velocity, gradient, rate=0.1):
    new_velocity = 0.9 * velocity + gradient
    return weight - rate * new_velocity, new_velocity


def adam_step(weight, state, gradient, rate=0.1):
    mean, square, step = state
    step = step + 1
    mean = 0.9 * mean + 0.1 * gradient
    square = 0.999 * square + 0.001 * gradient * gradient
    corrected_mean = mean / (1 - 0.9**step)
    corrected_square = square / (1 - 0.999**step)
    updated = weight - rate * corrected_mean / (jnp.sqrt(corrected_square) + 1e-8)
    return updated, (mean, square, step)


zero_state = (jnp.float64(0.0), jnp.float64(0.0), jnp.int64(0))


def main():
    # Case 1: Momentum remembers
    fresh, v0 = momentum_step(0.0, 0.0, 2.0)
    continued, v1 = momentum_step(0.0, 1.0, 2.0)
    close(fresh, -0.2)
    close(continued, -0.29)
    close(v1, 2.9)

    # Case 2: Audit Adam's first correction
    weight, state = adam_step(0.0, zero_state, 2.0)
    close(state[0], 0.2)
    close(state[1], 0.004)
    assert int(state[2]) == 1
    close(weight, -0.2 / (2.0 + 1e-8))

    # Case 3: Trace plain SGD
    close(1.0 - 0.2 * jnp.float64(3.0), 0.4)

    # Case 4: Continue momentum
    w, v = momentum_step(0.0, 0.0, 2.0)
    w, v = momentum_step(w, v, 2.0)
    close(w, -0.58)
    close(v, 3.8)

    # Case 5: Continue Adam's counter
    w, s = adam_step(0.0, zero_state, 2.0)
    w, s = adam_step(w, s, 2.0)
    assert int(s[2]) == 2
    close(w, -2 * 0.2 / (2.0 + 1e-8))

    # Case 6: Preserve zero-gradient history
    w, s = adam_step(0.0, zero_state, 2.0)
    next_w, next_s = adam_step(w, s, 0.0)
    assert float(next_w) < float(w)
    assert int(next_s[2]) == 2

    # Case 7: Compile the transition
    a, sa = adam_step(0.0, zero_state, 2.0)
    b, sb = jax.jit(adam_step)(0.0, zero_state, 2.0)
    close(a, b)
    for x, y in zip(sa, sb):
        close(x, y)

    # Case 8: Reverse the gradient
    w, s = adam_step(0.0, zero_state, -2.0)
    close(w, 0.2 / (2.0 + 1e-8))
    close(s[0], -0.2)
    close(s[1], 0.004)

    print("jax-014" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
