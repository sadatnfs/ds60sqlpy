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


def sample_objective(mean, scale, noise):
    return jnp.mean((mean + scale * noise) ** 2)


control = jnp.array([-1.0, 1.0])
noise = jax.random.normal(jax.random.key(61), (1024,), dtype=jnp.float64)


def main():
    # Case 1: An exact fixed-sample control
    value, gradients = jax.value_and_grad(sample_objective, argnums=(0, 1))(2.0, 3.0, control)
    close(value, 13.0)
    close(gradients[0], 4.0)
    close(gradients[1], 6.0)

    # Case 2: Inspect a real sampled estimate
    value, gradients = jax.value_and_grad(sample_objective, argnums=(0, 1))(2.0, 3.0, noise)
    assert bool(jnp.isfinite(value))
    close(gradients[0], 2 * jnp.mean(2.0 + 3.0 * noise))
    close(gradients[1], 2 * jnp.mean((2.0 + 3.0 * noise) * noise))

    # Case 3: Reuse draws in a derivative check
    h = 1e-5
    finite = (sample_objective(2.0 + h, 3.0, noise) - sample_objective(2.0 - h, 3.0, noise)) / (
        2 * h
    )
    close(finite, jax.grad(sample_objective)(2.0, 3.0, noise), atol=1e-7, rtol=0.0)

    # Case 4: Parameterize a positive scale
    function = lambda log_scale: sample_objective(2.0, jnp.exp(log_scale), control)
    close(jax.grad(function)(math.log(3.0)), 18.0)

    # Case 5: Check a zero-mean population formula
    close(sample_objective(0.0, 2.0, control), 4.0)
    close(jax.grad(sample_objective)(0.0, 2.0, control), 0.0)

    # Case 6: Retain the Monte Carlo count
    draws = (2.0 + 3.0 * noise) ** 2
    count = draws.size
    se = jnp.sqrt(jnp.var(draws, ddof=1) / count)
    assert count == 1024
    assert bool(jnp.isfinite(se)) and float(se) >= 0.0

    # Case 7: Vectorize parameter comparisons
    values = jax.vmap(lambda mean: sample_objective(mean, 3.0, control))(jnp.array([0.0, 1.0, 2.0]))
    close(values, [9.0, 10.0, 13.0])

    # Case 8: Replay the sampled input
    again = jax.random.normal(jax.random.key(61), (1024,), dtype=jnp.float64)
    close(again, noise)
    close(sample_objective(2.0, 3.0, again), sample_objective(2.0, 3.0, noise))

    print("jax-021" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
