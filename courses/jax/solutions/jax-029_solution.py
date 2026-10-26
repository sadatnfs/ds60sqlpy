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


def admit_attention(query, keys, values, allowed):
    if query.ndim != 2 or keys.ndim != 2 or values.ndim != 2:
        raise ValueError("matrices required")
    if query.shape[1] <= 0 or query.shape[1] != keys.shape[1] or keys.shape[0] != values.shape[0]:
        raise ValueError("attention feature/source shapes disagree")
    if allowed.shape != (query.shape[0], keys.shape[0]) or np.asarray(allowed).dtype != np.bool_:
        raise ValueError("Boolean query-key mask required")
    if not np.asarray(allowed).any(axis=1).all():
        raise ValueError("a query has no allowed key")


def attention(query, keys, values, allowed):
    scores = query @ keys.T / jnp.sqrt(query.shape[1])
    weights = jax.nn.softmax(jnp.where(allowed, scores, -jnp.inf), axis=-1)
    return weights @ values


q = jnp.zeros((3, 2))
k = jnp.zeros((3, 2))
v = jnp.array([[2.0, 0.0], [0.0, 2.0], [6.0, 6.0]])
mask = jnp.tril(jnp.ones((3, 3), dtype=bool))


def adapter_loss(a, b):
    output = jnp.ones((1, 8)) @ (jnp.eye(8) + 2.0 * a @ b)
    return jnp.mean(output**2)


a = jnp.full((8, 2), 1 / 8)
b = jnp.zeros((2, 8))


def main():
    # Case 1: An exact causal average
    admit_attention(q, k, v, mask)
    close(attention(q, k, v, mask), [[2.0, 0.0], [1.0, 1.0], [8 / 3, 8 / 3]])

    # Case 2: A complete low-rank first step
    ga, gb = jax.grad(adapter_loss, argnums=(0, 1))(a, b)
    close(ga, jnp.zeros_like(a))
    close(gb, jnp.full_like(b, 0.5))
    close(adapter_loss(a, b), 1.0)
    close(adapter_loss(a, b - 0.1 * gb), 0.64)

    # Case 3: Perturb only the future
    changed = v.at[2].set(jnp.array([100.0, 200.0]))
    close(attention(q, k, changed, mask)[:2], attention(q, k, v, mask)[:2])

    # Case 4: Test the scale with nonuniform scores
    query = jnp.array([[1.0, 0.0]])
    keys = jnp.eye(2)
    values = 2 * jnp.eye(2)
    probability = 1 / (1 + math.exp(-1 / math.sqrt(2)))
    close(
        attention(query, keys, values, jnp.ones((1, 2), dtype=bool)),
        [[2 * probability, 2 * (1 - probability)]],
    )

    # Case 5: Refuse an empty allowed set
    try:
        admit_attention(q, k, v, mask.at[0].set(False))
    except ValueError:
        pass
    else:
        raise AssertionError("all-masked query admitted")

    # Case 6: Trace value gradients
    g = jax.grad(lambda values: attention(q, k, values, mask).sum())(v)
    close(g, [[11 / 6, 11 / 6], [5 / 6, 5 / 6], [1 / 3, 1 / 3]])

    # Case 7: Count and bound the adapter
    assert a.size + b.size == 32
    assert np.linalg.matrix_rank(np.asarray(a @ b)) <= 2

    # Case 8: Compile the admitted operation
    close(jax.jit(attention)(q, k, v, mask), attention(q, k, v, mask))

    print("jax-029" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
