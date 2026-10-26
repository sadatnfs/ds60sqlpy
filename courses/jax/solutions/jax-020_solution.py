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


def simulate(rate, initial=1.0, *, steps=10, horizon=1.0):
    dt = horizon / steps

    def transition(value, unused):
        updated = value * (1 - rate * dt)
        return updated, updated

    return jax.lax.scan(transition, jnp.asarray(initial, dtype=jnp.float64), xs=None, length=steps)[
        0
    ]


def main():
    # Case 1: Check the discretized value
    value = simulate(1.0)
    close(value, 0.9**10)
    assert float(value) < math.exp(-1.0)

    # Case 2: Refine at the same horizon
    error10 = abs(float(simulate(1.0, steps=10)) - math.exp(-1.0))
    error20 = abs(float(simulate(1.0, steps=20)) - math.exp(-1.0))
    assert error20 < error10

    # Case 3: Differentiate the implemented algorithm
    close(jax.grad(simulate)(1.0), -(0.9**9))

    # Case 4: Compare continuous sensitivity
    continuous = -math.exp(-1.0)
    discrete = float(jax.grad(simulate)(1.0))
    assert not np.isclose(continuous, discrete, atol=1e-4, rtol=0.0)

    # Case 5: Refine the derivative
    exact = -math.exp(-1.0)
    a = abs(float(jax.grad(lambda k: simulate(k, steps=10))(1.0)) - exact)
    b = abs(float(jax.grad(lambda k: simulate(k, steps=20))(1.0)) - exact)
    assert b < a

    # Case 6: Check zero rate
    close(simulate(0.0, initial=3.0), 3.0)

    # Case 7: Differentiate the initial state
    close(jax.grad(lambda initial: simulate(1.0, initial=initial))(2.0), 0.9**10)

    # Case 8: Inspect an unstable numerical regime
    close(simulate(3.0, steps=1), -2.0)
    assert math.exp(-3.0) > 0.0

    print("jax-020" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
