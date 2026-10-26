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


def global_mean(local_sum, local_count):
    total = jax.lax.psum(local_sum, "replica")
    count = jax.lax.psum(local_count, "replica")
    return total / count


mapped_mean = jax.vmap(global_mean, in_axes=(0, 0), axis_name="replica")
local_sums = jnp.array([2.0, 12.0])
local_counts = jnp.array([1.0, 3.0])


def main():
    # Case 1: Combine unequal shards correctly
    close(mapped_mean(local_sums, local_counts), [3.5, 3.5])
    close(jnp.mean(local_sums / local_counts), 3.0)

    # Case 2: Aggregate gradient sums
    combined = mapped_mean(jnp.array([-4.0, -116.0]), local_counts)
    close(combined, [-30.0, -30.0])
    x = jnp.array([1.0, 2.0, 3.0, 4.0])
    full = jax.grad(lambda w: jnp.mean((w * x - 2 * x) ** 2))(0.0)
    close(full, -30.0)

    # Case 3: Check equal counts
    close(mapped_mean(jnp.array([2.0, 6.0]), jnp.array([2.0, 2.0])), [2.0, 2.0])

    # Case 4: Add a zero-count participant
    close(mapped_mean(jnp.array([2.0, 12.0, 0.0]), jnp.array([1.0, 3.0, 0.0])), [3.5, 3.5, 3.5])

    # Case 5: Gather participant identity
    gather = jax.vmap(lambda x: jax.lax.all_gather(x, "replica"), axis_name="replica")
    close(gather(jnp.array([2.0, 5.0])), [[2.0, 5.0], [2.0, 5.0]])

    # Case 6: Check a global sum
    summed = jax.vmap(lambda x: jax.lax.psum(x, "replica"), axis_name="replica")
    close(summed(jnp.array([2.0, 5.0, 7.0])), [14.0, 14.0, 14.0])

    # Case 7: Compile the collective model
    close(jax.jit(mapped_mean)(local_sums, local_counts), [3.5, 3.5])

    # Case 8: Detect the wrong weighting
    wrong = jnp.mean(jnp.array([-4.0, -116.0]) / local_counts)
    assert not np.isclose(float(wrong), -30.0)

    print("jax-028" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
