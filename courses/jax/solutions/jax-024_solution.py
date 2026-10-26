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


def gram(values):
    return values.T @ values


values = jnp.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])


def main():
    # Case 1: Infer an output interface
    shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((3, 2), jnp.float64))
    assert shape.shape == (2, 2)
    assert shape.dtype == jnp.float64

    # Case 2: Lower, compile and execute
    lowered = jax.jit(gram).lower(values)
    compiled = lowered.compile()
    close(compiled(values), [[35.0, 44.0], [44.0, 56.0]])

    # Case 3: Change only the abstract row count
    shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((7, 2), jnp.float64))
    assert shape.shape == (2, 2)

    # Case 4: Change the feature count
    shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((3, 4), jnp.float64))
    assert shape.shape == (4, 4)

    # Case 5: Inspect staged dependencies
    closed = jax.make_jaxpr(gram)(values)
    assert len(closed.jaxpr.outvars) == 1
    assert closed.jaxpr.eqns

    # Case 6: Execute another compatible value
    compiled = jax.jit(gram).lower(values).compile()
    close(compiled(2 * values), 4 * gram(values))

    # Case 7: Compose a scalar sensitivity
    close(jax.grad(lambda x: gram(x).sum())(values), [[6.0, 6.0], [14.0, 14.0], [22.0, 22.0]])

    # Case 8: Separate metadata from values
    zero = jnp.zeros_like(values)
    result = jax.jit(gram)(zero)
    assert result.shape == (2, 2)
    close(result, jnp.zeros((2, 2)))

    print("jax-024" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
