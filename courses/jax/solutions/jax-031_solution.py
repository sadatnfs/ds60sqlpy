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


train_x = jnp.array([-2.0, -1.0, 0.0, 1.0, 2.0])
heldout_x = jnp.array([-1.5, -0.5, 0.5, 1.5])


def targets(values):
    return 1 + 2 * values - 0.5 * values * values


def features(values):
    return jnp.stack((jnp.ones_like(values), values, values * values), axis=1)


train_design = features(train_x)
train_y = targets(train_x)
heldout_design = features(heldout_x)
heldout_y = targets(heldout_x)


def loss(weight, design, labels):
    return jnp.mean((design @ weight - labels) ** 2)


def advance(weight, steps):
    def update(state, unused):
        gradient = jax.grad(loss)(state, train_design, train_y)
        state = state - 0.02 * gradient
        return state, loss(state, train_design, train_y)

    return jax.lax.scan(update, weight, xs=None, length=steps)


trained = jax.jit(lambda w: advance(w, 400))(jnp.zeros(3))[0]


def main():
    # Case 1: Fit a bounded candidate
    close(trained, [1.0, 2.0, -0.5], atol=0.01, rtol=0.0)
    assert float(loss(trained, train_design, train_y)) < float(
        loss(jnp.zeros(3), train_design, train_y)
    )

    # Case 2: Compare on fixed held-out inputs
    affine_train = train_design[:, :2]
    affine = jnp.linalg.lstsq(affine_train, train_y, rcond=None)[0]
    affine_error = loss(affine, heldout_design[:, :2], heldout_y)
    quadratic_error = loss(trained, heldout_design, heldout_y)
    assert float(quadratic_error) < float(affine_error)
    print(
        {
            "quadratic_holdout_mse": float(quadratic_error),
            "affine_holdout_mse": float(affine_error),
            "holdout_count": 4,
        }
    )

    # Case 3: Audit the initial gradient
    zero = jnp.zeros(3)
    explicit = 2 * train_design.T @ (train_design @ zero - train_y) / train_y.size
    close(jax.grad(loss)(zero, train_design, train_y), explicit)

    # Case 4: Check an independent optimum
    optimum = jnp.linalg.lstsq(train_design, train_y, rcond=None)[0]
    close(optimum, [1.0, 2.0, -0.5])

    # Case 5: Replay the fixed budget
    again = jax.jit(lambda w: advance(w, 400))(jnp.zeros(3))[0]
    close(again, trained)

    # Case 6: Resume a partial trajectory
    first = advance(jnp.zeros(3), 200)[0]
    continued = advance(first, 200)[0]
    close(continued, trained)

    # Case 7: Verify the held-out split
    assert not set(np.asarray(train_x).tolist()) & set(np.asarray(heldout_x).tolist())

    # Case 8: Transfer the coefficient rule
    oracle = jnp.array([1.0, 2.0, -0.5])
    close(features(jnp.array([3.0])) @ oracle, [2.5])

    print("jax-031" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
