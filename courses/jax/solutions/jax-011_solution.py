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


def recurrence(initial, values):
    def step(carry, value):
        updated = 0.5 * carry + value
        return updated, updated

    return jax.lax.scan(step, initial, values)


def branch(value):
    return jax.lax.cond(value >= 0.0, lambda x: x * x, lambda x: -x, value)


def main():
    # Case 1: Trace a scan
    last, history = recurrence(jnp.float64(0.0), jnp.array([2.0, 2.0, 2.0]))
    close(last, 3.5)
    close(history, [2.0, 3.0, 3.5])

    # Case 2: Branch on a runtime value
    compiled = jax.jit(branch)
    close(compiled(jnp.float64(2.0)), 4.0)
    close(compiled(jnp.float64(-2.0)), 2.0)

    # Case 3: Differentiate the initial carry
    values = jnp.array([2.0, 2.0, 2.0])
    close(jax.grad(lambda h: recurrence(h, values)[0])(0.0), 0.125)

    # Case 4: Differentiate sequence inputs
    close(
        jax.grad(lambda values: recurrence(jnp.float64(0.0), values)[0])(
            jnp.array([2.0, 2.0, 2.0])
        ),
        [0.25, 0.5, 1.0],
    )

    # Case 5: Handle an empty scan
    last, history = recurrence(jnp.float64(5.0), jnp.array([], dtype=jnp.float64))
    close(last, 5.0)
    assert history.shape == (0,)

    # Case 6: Use a fixed-index loop
    result = jax.lax.fori_loop(0, 4, lambda i, total: total + i, jnp.int64(0))
    assert int(result) == 6

    # Case 7: Inspect a dynamic stopping rule
    def double_until(value):
        return jax.lax.while_loop(lambda z: z < 10.0, lambda z: 2.0 * z, value)

    value, tangent = jax.jvp(double_until, (jnp.float64(1.0),), (jnp.float64(1.0),))
    close(value, 16.0)
    close(tangent, 16.0)

    # Case 8: Transfer to a batched state
    last, history = recurrence(jnp.zeros(2), jnp.array([[2.0, 4.0], [1.0, 2.0]]))
    close(last, [2.0, 4.0])
    assert history.shape == (2, 2)

    print("jax-011" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
