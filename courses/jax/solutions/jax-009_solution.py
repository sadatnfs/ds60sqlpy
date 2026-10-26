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


def quadratic(value):
    a, b = value
    return a * a + a * b + 2 * b * b


point = jnp.array([1.0, 2.0])
expected_hessian = jnp.array([[2.0, 1.0], [1.0, 4.0]])


def main():
    # Case 1: Inspect every curvature entry
    hessian = jax.jacfwd(jax.grad(quadratic))(point)
    close(hessian, expected_hessian)
    close(hessian, hessian.T)

    # Case 2: Ask only for the needed product
    direction = jnp.array([2.0, -1.0])
    product = jax.jvp(jax.grad(quadratic), (point,), (direction,))[1]
    close(product, [3.0, -2.0])
    close(product, expected_hessian @ direction)

    # Case 3: Check the first derivative
    close(jax.grad(quadratic)(point), [4.0, 9.0])

    # Case 4: Reverse the transform order
    close(jax.jacrev(jax.grad(quadratic))(point), expected_hessian)

    # Case 5: Check a matrix-free product numerically
    v, h = jnp.array([2.0, -1.0]), 1e-5
    gradient = jax.grad(quadratic)
    finite = (gradient(point + h * v) - gradient(point - h * v)) / (2 * h)
    close(finite, [3.0, -2.0], atol=1e-8, rtol=0.0)

    # Case 6: Interpret directional curvature
    v = jnp.array([2.0, -1.0])
    close(jnp.vdot(v, expected_hessian @ v), 8.0)

    # Case 7: Change the evaluation point
    close(jax.hessian(quadratic)(jnp.array([-3.0, 7.0])), expected_hessian)

    # Case 8: Contrast nonlinear curvature
    second = jax.grad(jax.grad(lambda z: z**4))
    close(second(0.0), 0.0)
    close(second(2.0), 48.0)

    print("jax-009" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
