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


x = jnp.array([1.0, 2.0, 3.0])
y = 2 * x


def loss(weight):
    return jnp.mean((weight * x - y) ** 2)


def main():
    # Case 1: Four quantities in one update
    value, gradient = jax.value_and_grad(loss)(jnp.float64(0.0))
    updated = -0.1 * gradient
    close(value, 56 / 3)
    close(gradient, -56 / 3)
    close(updated, 28 / 15)
    close(loss(updated), 56 / 675)

    # Case 2: Same forward value, different derivative
    ordinary = lambda z: z * z
    stopped = lambda z: jax.lax.stop_gradient(z) ** 2
    close(ordinary(3.0), stopped(3.0))
    close(jax.grad(ordinary)(3.0), 6.0)
    close(jax.grad(stopped)(3.0), 0.0)

    # Case 3: Check another smooth point
    close(jax.grad(loss)(1.0), -28 / 3)

    # Case 4: Use a central difference
    w, h = 0.7, 1e-5
    numerical = (loss(w + h) - loss(w - h)) / (2 * h)
    close(numerical, jax.grad(loss)(w), atol=1e-8, rtol=0.0)

    # Case 5: Change the reduction
    summed = lambda w: jnp.sum((w * x - y) ** 2)
    close(jax.grad(summed)(0.0), -56.0)

    # Case 6: Inspect the optimum
    value, gradient = jax.value_and_grad(loss)(2.0)
    close(value, 0.0)
    close(gradient, 0.0)

    # Case 7: Differentiate a parameter tree
    def affine_loss(p):
        return jnp.mean((p["weight"] * x + p["bias"] - y) ** 2)

    g = jax.grad(affine_loss)({"weight": jnp.float64(0.0), "bias": jnp.float64(0.0)})
    close(g["weight"], -56 / 3)
    close(g["bias"], -8.0)

    # Case 8: Choose a scalar objective
    vector_loss = lambda w: (w * x - y) ** 2
    try:
        jax.grad(vector_loss)(0.0)
    except TypeError:
        pass
    else:
        raise AssertionError("vector objective accepted")
    close(jax.grad(lambda w: vector_loss(w).mean())(0.0), -56 / 3)

    print("jax-007" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
