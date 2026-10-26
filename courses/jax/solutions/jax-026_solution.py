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


def cubic_sum(values):
    return jnp.sum(values**3)


rematerialized = jax.checkpoint(cubic_sum)
consume = jax.jit(lambda values: values + 1.0, donate_argnums=(0,))


def main():
    # Case 1: Check recomputed derivatives
    values = jnp.array([1.0, 2.0, 3.0])
    close(rematerialized(values), 36.0)
    close(jax.grad(rematerialized)(values), [3.0, 12.0, 27.0])
    close(jax.grad(cubic_sum)(values), jax.grad(rematerialized)(values))

    # Case 2: Consume and replace a buffer
    values = jnp.array([1.0, 2.0, 3.0])
    expected = np.array(values) + 1.0
    updated = consume(values)
    updated.block_until_ready()
    close(updated, expected)

    # Case 3: Change the derivative input
    close(jax.grad(rematerialized)(jnp.array([-2.0, 0.0, 2.0])), [12.0, 0.0, 12.0])

    # Case 4: Compose checkpointing with JIT
    close(jax.jit(jax.grad(rematerialized))(jnp.array([1.0, 2.0, 3.0])), [3.0, 12.0, 27.0])

    # Case 5: Continue from returned ownership
    state = jnp.array([1.0, 2.0])
    state = consume(state)
    state = consume(state)
    close(state, [3.0, 4.0])

    # Case 6: Keep an ordinary baseline
    baseline = jnp.array([4.0, 5.0]) + 1.0
    updated = consume(jnp.array([4.0, 5.0]))
    close(updated, baseline)

    # Case 7: Check a higher derivative
    hessian = jax.hessian(rematerialized)(jnp.array([1.0, 2.0]))
    close(hessian, [[6.0, 0.0], [0.0, 12.0]])

    # Case 8: Separate a resource claim
    result = consume(jnp.zeros(4, dtype=jnp.float64))
    assert result.size == 4 and result.nbytes == 32

    print("jax-026" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
