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


def predict_one(weight, features):
    return jnp.vdot(weight, features)


def loss_one(weight, features, target):
    return (predict_one(weight, features) - target) ** 2


features = jnp.array([[1.0, 2.0], [3.0, 4.0]])
targets = jnp.array([1.0, 2.0])


def main():
    # Case 1: Share one model across rows
    predict_batch = jax.vmap(predict_one, in_axes=(None, 0))
    close(predict_batch(jnp.array([2.0, -1.0]), features), [0.0, 2.0])

    # Case 2: Retain per-example derivatives
    per_example = jax.vmap(jax.grad(loss_one), in_axes=(None, 0, 0))
    close(per_example(jnp.zeros(2), features, targets), [[-2.0, -4.0], [-12.0, -16.0]])

    # Case 3: Compare with a literal loop
    w = jnp.array([2.0, -1.0])
    loop = jnp.stack([predict_one(w, row) for row in features])
    close(jax.vmap(predict_one, in_axes=(None, 0))(w, features), loop)

    # Case 4: Reduce gradients deliberately
    batch_loss = lambda w: jnp.mean(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))
    close(jax.grad(batch_loss)(jnp.zeros(2)), [-7.0, -10.0])

    # Case 5: Change to a sum
    summed = lambda w: jnp.sum(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))
    close(jax.grad(summed)(jnp.zeros(2)), [-14.0, -20.0])

    # Case 6: Map several models
    weights = jnp.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    close(jax.vmap(predict_one, in_axes=(0, None))(weights, jnp.array([2.0, 3.0])), [2.0, 3.0, 5.0])

    # Case 7: Compose with JIT
    compiled = jax.jit(jax.vmap(predict_one, in_axes=(None, 0)))
    close(compiled(jnp.array([2.0, -1.0]), features), [0.0, 2.0])

    # Case 8: Allocate random streams per row
    keys = jax.random.split(jax.random.key(23), 3)
    draw = jax.vmap(lambda key: jax.random.normal(key, (2,)))
    a, b = draw(keys), draw(keys)
    assert a.shape == (3, 2)
    close(a, b)

    print("jax-012" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
