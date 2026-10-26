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


def function(value):
    a, b = value
    return jnp.stack((a * a, a * b, jnp.sin(b)))


point = jnp.array([2.0, 0.0])
jacobian = jnp.array([[4.0, 0.0], [0.0, 2.0], [0.0, 1.0]])


def main():
    # Case 1: Push one input direction
    value, tangent = jax.jvp(function, (point,), (jnp.array([3.0, 4.0]),))
    close(value, [4.0, 0.0, 0.0])
    close(tangent, [12.0, 8.0, 4.0])

    # Case 2: Pull back an output weighting
    value, pullback = jax.vjp(function, point)
    (input_cotangent,) = pullback(jnp.array([1.0, 2.0, 3.0]))
    close(input_cotangent, [4.0, 7.0])

    # Case 3: Probe the first input coordinate
    close(jax.jvp(function, (point,), (jnp.array([1.0, 0.0]),))[1], [4.0, 0.0, 0.0])

    # Case 4: Probe the second output coordinate
    _, back = jax.vjp(function, point)
    close(back(jnp.array([0.0, 1.0, 0.0]))[0], [0.0, 2.0])

    # Case 5: Check duality
    v, u = jnp.array([3.0, 4.0]), jnp.array([1.0, 2.0, 3.0])
    jv = jax.jvp(function, (point,), (v,))[1]
    _, back = jax.vjp(function, point)
    close(jnp.vdot(u, jv), 40.0)
    close(jnp.vdot(v, back(u)[0]), 40.0)

    # Case 6: Check a directional finite difference
    direction, h = jnp.array([3.0, 4.0]), 1e-5
    finite = (function(point + h * direction) - function(point - h * direction)) / (2 * h)
    close(finite, jacobian @ direction, atol=1e-8, rtol=0.0)

    # Case 7: Change the point
    close(
        jax.jacfwd(function)(jnp.array([1.0, 1.0])), [[2.0, 0.0], [1.0, 1.0], [0.0, math.cos(1.0)]]
    )

    # Case 8: Recover a scalar gradient
    weights = jnp.array([1.0, 2.0, 3.0])
    close(jax.grad(lambda z: jnp.vdot(weights, function(z)))(point), [4.0, 7.0])

    print("jax-008" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
