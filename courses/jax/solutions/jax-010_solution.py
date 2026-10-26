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


def repeat_add(value, n):
    result = 0.0 * value
    for _ in range(n):
        result = result + value
    return result


compiled_repeat = jax.jit(repeat_add, static_argnames=("n",))


def main():
    # Case 1: A deliberate static loop
    close(compiled_repeat(2.0, n=3), 6.0)
    close(compiled_repeat(2.0, n=4), 8.0)

    # Case 2: Trace-time effects are not runtime counters
    traces = []

    def observed(z):
        traces.append(z.shape)
        return z + 1

    compiled = jax.jit(observed)
    close(compiled(jnp.array([1.0, 2.0])), [2.0, 3.0])
    close(compiled(jnp.array([4.0, 5.0])), [5.0, 6.0])
    assert traces == [(2,)]

    # Case 3: Compare eager and compiled values
    function = lambda z: z * z + z + 1
    values = jnp.array([1.0, 2.0, 3.0])
    close(function(values), [3.0, 7.0, 13.0])
    close(jax.jit(function)(values), function(values))

    # Case 4: Observe a shape specialization
    traces = []

    def shaped(z):
        traces.append(z.shape)
        return z * 2

    compiled = jax.jit(shaped)
    compiled(jnp.ones(2)).block_until_ready()
    compiled(jnp.ones(3)).block_until_ready()
    assert traces == [(2,), (3,)]

    # Case 5: Expose a traced Boolean error
    def bad(z):
        if z > 0:
            return z
        return -z

    try:
        jax.jit(bad)(jnp.float64(2.0))
    except jax.errors.TracerBoolConversionError:
        pass
    else:
        raise AssertionError("dynamic Python condition accepted")

    # Case 6: Keep zero iterations defined
    close(compiled_repeat(3.0, n=0), 0.0)

    # Case 7: Compose differentiation with compilation
    compiled_loss = jax.jit(lambda z: jnp.sum(z * z))
    close(jax.grad(compiled_loss)(jnp.array([1.0, 2.0])), [2.0, 4.0])

    # Case 8: Inspect the staged operations
    closed = jax.make_jaxpr(lambda z: z * z + 1)(jnp.float64(2.0))
    assert len(closed.jaxpr.eqns) >= 1
    assert len(closed.jaxpr.outvars) == 1

    print("jax-010" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
