"""Small offline JAX mechanism investigation; CPU evidence only."""

from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp

from jax.experimental import checkify

# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)


def safe_log_extension(values):
    positive = values > 0.0
    safe_inputs = jnp.where(positive, values, 1.0)
    return jnp.where(positive, jnp.log(safe_inputs), 0.0)


def main():
    # Case 1: Repair an undefined intermediate
    values = jnp.array([-1.0, 0.0, 2.0])
    close(safe_log_extension(values), [0.0, 0.0, math.log(2.0)])
    g = jax.grad(lambda x: safe_log_extension(x).sum())(values)
    close(g, [0.0, 0.0, 0.5])
    assert bool(jnp.isfinite(g).all())

    # Case 2: Carry a dynamic check
    def checked(values):
        checkify.check(jnp.all(values > 0.0), "positive inputs required")
        return values.sum()

    run = jax.jit(checkify.checkify(checked))
    good, total = run(jnp.array([1.0, 2.0]))
    bad, _ = run(jnp.array([1.0, -2.0]))
    assert good.get() is None
    assert bad.get() is not None
    close(total, 3.0)

    # Case 3: Expose a host conversion
    try:
        jax.jit(lambda x: np.asarray(x) + 1)(jnp.ones(2))
    except jax.errors.TracerArrayConversionError:
        pass
    else:
        raise AssertionError("host conversion accepted")

    # Case 4: Expose a dynamic output length
    try:
        jax.jit(lambda x: x[x > 0.0])(jnp.array([-1.0, 2.0]))
    except jax.errors.NonConcreteBooleanIndexError:
        pass
    else:
        raise AssertionError("dynamic shape accepted")

    # Case 5: Use a fixed-shape alternative
    function = jax.jit(lambda x: jnp.where(x > 0.0, x, 0.0).sum())
    close(function(jnp.array([-1.0, 2.0])), 2.0)

    # Case 6: Print a runtime diagnostic
    def observed(x):
        total = x.sum()
        jax.debug.print("total={total}", total=total)
        return total

    close(jax.jit(observed)(jnp.array([1.0, 2.0])), 3.0)

    # Case 7: Compare with JIT disabled
    function = jax.jit(lambda x: x * x + 1)
    with jax.disable_jit():
        eager = function(jnp.array([1.0, 2.0]))
    close(function(jnp.array([1.0, 2.0])), eager)

    # Case 8: Retain the positive-domain derivative
    close(
        jax.grad(lambda x: safe_log_extension(x).sum())(jnp.array([1.0, 2.0, 4.0])),
        [1.0, 0.5, 0.25],
    )

    print("jax-018" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
