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


def initialize(key):
    first, second = jax.random.split(key)
    return {
        "w1": 0.3 * jax.random.normal(first, (1, 4), dtype=jnp.float64),
        "b1": jnp.zeros(4),
        "w2": 0.3 * jax.random.normal(second, (4, 1), dtype=jnp.float64),
        "b2": jnp.zeros(1),
    }


def forward(parameters, inputs):
    hidden = jnp.tanh(inputs @ parameters["w1"] + parameters["b1"])
    return hidden @ parameters["w2"] + parameters["b2"]


def objective(parameters, inputs, labels):
    return jnp.mean((forward(parameters, inputs) - labels) ** 2)


def step(parameters, inputs, labels):
    gradients = jax.grad(objective)(parameters, inputs, labels)
    return jax.tree.map(lambda p, g: p - 0.05 * g, parameters, gradients)


compiled_step = jax.jit(step)
train_x = jnp.array([[-1.0], [-0.5], [0.0], [0.5], [1.0]])
train_y = jnp.tanh(2 * train_x)
heldout_x = jnp.array([[-0.75], [0.75]])
heldout_y = jnp.tanh(2 * heldout_x)


def train():
    parameters = initialize(jax.random.key(31))
    for _ in range(120):
        parameters = compiled_step(parameters, train_x, train_y)
    return parameters


def main():
    # Case 1: Trace the architecture
    parameters = initialize(jax.random.key(31))
    assert sum(x.size for x in jax.tree.leaves(parameters)) == 13
    predictions = forward(parameters, train_x)
    assert predictions.shape == train_y.shape == (5, 1)
    assert bool(jnp.isfinite(predictions).all())

    # Case 2: A bounded optimization observation
    initial = initialize(jax.random.key(31))
    trained = train()
    before = objective(initial, train_x, train_y)
    after = objective(trained, train_x, train_y)
    assert bool(jnp.isfinite(after))
    assert float(after) < float(before)

    # Case 3: Replay initialization
    a = initialize(jax.random.key(31))
    b = initialize(jax.random.key(31))
    for x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):
        close(x, y)

    # Case 4: Inspect gradients
    p = initialize(jax.random.key(31))
    g = jax.grad(objective)(p, train_x, train_y)
    assert jax.tree.structure(p) == jax.tree.structure(g)
    for a, b in zip(jax.tree.leaves(p), jax.tree.leaves(g)):
        assert a.shape == b.shape
        assert bool(jnp.isfinite(b).all())
    assert sum(float(jnp.vdot(x, x)) for x in jax.tree.leaves(g)) > 0.0

    # Case 5: Check one compiled update
    p = initialize(jax.random.key(31))
    a, b = step(p, train_x, train_y), compiled_step(p, train_x, train_y)
    for x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):
        close(x, y)

    # Case 6: Evaluate untouched inputs
    p = train()
    value = objective(p, heldout_x, heldout_y)
    assert heldout_x.shape[0] == 2
    assert bool(jnp.isfinite(value)) and float(value) >= 0.0

    # Case 7: Separate training from inference
    p = train()
    a, b = forward(p, heldout_x), forward(p, heldout_x)
    close(a, b)

    # Case 8: Check an architecture change
    count = lambda width: width + width + width + 1
    assert count(4) == 13 and count(5) == 16

    print("jax-015" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
