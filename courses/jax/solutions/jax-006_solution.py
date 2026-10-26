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


params = {"weight": jnp.array([[1.0, 2.0], [3.0, 4.0]]), "bias": jnp.array([1.0, -1.0])}


def checked_update(parameters, gradients, rate):
    if jax.tree.structure(parameters) != jax.tree.structure(gradients):
        raise ValueError("gradient tree differs")
    for p, g in zip(jax.tree.leaves(parameters), jax.tree.leaves(gradients)):
        if p.shape != g.shape:
            raise ValueError("gradient leaf shape differs")
    return jax.tree.map(lambda p, g: p - rate * g, parameters, gradients)


def main():
    # Case 1: Map an update over a tree
    gradients = jax.tree.map(jnp.ones_like, params)
    updated = checked_update(params, gradients, 0.1)
    close(updated["weight"], [[0.9, 1.9], [2.9, 3.9]])
    close(updated["bias"], [0.9, -1.1])
    close(params["bias"], [1.0, -1.0])

    # Case 2: Reject a misleading broadcast
    wrong = {"weight": jnp.ones((2, 2)), "bias": jnp.float64(1.0)}
    try:
        checked_update(params, wrong, 0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("bad leaf shape accepted")

    # Case 3: Inspect the leaf ledger
    shapes = jax.tree.map(lambda x: x.shape, params)
    assert shapes == {"weight": (2, 2), "bias": (2,)}

    # Case 4: Count stored scalars
    assert sum(x.size for x in jax.tree.leaves(params)) == 6

    # Case 5: Reconstruct the tree
    leaves, structure = jax.tree.flatten(params)
    restored = jax.tree.unflatten(structure, leaves)
    assert jax.tree.structure(restored) == jax.tree.structure(params)
    close(restored["weight"], params["weight"])

    # Case 6: Reject a missing field
    try:
        checked_update(params, {"weight": jnp.ones((2, 2))}, 0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("missing leaf accepted")

    # Case 7: Apply distinct gradients
    g = {"weight": jnp.full((2, 2), 2.0), "bias": jnp.array([3.0, -4.0])}
    u = checked_update(params, g, 0.5)
    close(u["weight"], [[0.0, 1.0], [2.0, 3.0]])
    close(u["bias"], [-0.5, 1.0])

    # Case 8: Transfer to nested state
    state = (params, jnp.int64(4))
    zero = jax.tree.map(jnp.zeros_like, state)
    assert jax.tree.structure(zero) == jax.tree.structure(state)
    assert all(bool(jnp.all(x == 0)) for x in jax.tree.leaves(zero))

    print("jax-006" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
