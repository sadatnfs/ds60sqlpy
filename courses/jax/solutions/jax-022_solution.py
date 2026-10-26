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


@jax.custom_jvp
def stable_softplus(value):
    return jnp.logaddexp(0.0, value)


@stable_softplus.defjvp
def softplus_jvp(primals, tangents):
    (value,), (tangent,) = primals, tangents
    return stable_softplus(value), jax.nn.sigmoid(value) * tangent


@jax.custom_vjp
def custom_square(value):
    return value * value


def square_forward(value):
    return value * value, value


def square_backward(saved, cotangent):
    return (2 * saved * cotangent,)


custom_square.defvjp(square_forward, square_backward)


def main():
    # Case 1: A stable custom JVP
    value, tangent = jax.jvp(stable_softplus, (jnp.float64(0.0),), (jnp.float64(3.0),))
    close(value, math.log(2.0))
    close(tangent, 1.5)

    # Case 2: Propagate a non-unit cotangent
    value, back = jax.vjp(custom_square, jnp.float64(3.0))
    close(value, 9.0)
    close(back(jnp.float64(4.0))[0], 24.0)

    # Case 3: Compare an ordinary gradient
    points = jnp.array([-2.0, 0.0, 2.0])
    close(jax.vmap(jax.grad(stable_softplus))(points), jax.nn.sigmoid(points))

    # Case 4: Check tangent linearity
    jvp = lambda tangent: jax.jvp(stable_softplus, (jnp.float64(1.0),), (jnp.float64(tangent),))[1]
    close(jvp(5.0), jvp(2.0) + jvp(3.0))

    # Case 5: Check an extreme stable input
    close(stable_softplus(1000.0), 1000.0)
    close(jax.grad(stable_softplus)(1000.0), 1.0)

    # Case 6: Differentiate a composition
    close(jax.grad(lambda x: 4 * custom_square(x))(3.0), 24.0)

    # Case 7: Check a second derivative
    close(jax.grad(jax.grad(stable_softplus))(0.0), 0.25)

    # Case 8: Name the forward-mode limit
    try:
        jax.jvp(custom_square, (jnp.float64(3.0),), (jnp.float64(1.0),))
    except TypeError:
        pass
    else:
        raise AssertionError("unexpected custom_vjp forward-mode support")

    print("jax-022" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
