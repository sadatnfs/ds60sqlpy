"""Small offline JAX mechanism investigation; CPU evidence only."""

from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp

from time import perf_counter

# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)


def product(values):
    return values @ values.T


def completed_times(function, argument, repeats):
    if type(repeats) is not int or repeats <= 0:
        raise ValueError("positive integer repeats required")
    times = []
    result = None
    for _ in range(repeats):
        start = perf_counter()
        result = function(argument)
        result.block_until_ready()
        times.append(perf_counter() - start)
    return result, np.asarray(times)


values = jnp.arange(256.0, dtype=jnp.float64).reshape(16, 16) / 256.0


def main():
    # Case 1: Measure first and warm calls separately
    compiled = jax.jit(product)
    first, cold = completed_times(compiled, values, 1)
    last, warm = completed_times(compiled, values, 3)
    close(first, np.asarray(values) @ np.asarray(values).T)
    close(last, first)
    assert cold.shape == (1,) and warm.shape == (3,)
    assert np.isfinite(cold).all() and np.isfinite(warm).all()
    assert (cold >= 0).all() and (warm >= 0).all()
    print({"first_seconds": cold.tolist(), "warm_seconds": warm.tolist()})

    # Case 2: Keep placement outside a compute-only boundary
    host = np.arange(256.0, dtype=np.float64).reshape(16, 16) / 256.0
    placed = jax.device_put(host)
    placed.block_until_ready()
    result, times = completed_times(jax.jit(product), placed, 1)
    close(result, host @ host.T)
    assert np.isfinite(times).all()

    # Case 3: Reject an empty timing sample
    try:
        completed_times(product, values, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("empty timing accepted")

    # Case 4: Retain the shape contract
    result, times = completed_times(jax.jit(product), values, 1)
    assert result.shape == (16, 16)

    # Case 5: Compare eager and compiled outputs
    close(product(values), jax.jit(product)(values))

    # Case 6: Report a declared summary
    _, times = completed_times(jax.jit(product), values, 3)
    median = float(np.median(times))
    assert float(times.min()) <= median <= float(times.max())

    # Case 7: Change workload size explicitly
    small = jnp.arange(64.0, dtype=jnp.float64).reshape(8, 8) / 64.0
    result, _ = completed_times(jax.jit(product), small, 1)
    close(result, np.asarray(small) @ np.asarray(small).T)

    # Case 8: Identify the executed backend
    result = product(values)
    result.block_until_ready()
    assert jax.default_backend() == "cpu"
    assert all(device.platform == "cpu" for device in result.devices())

    print("jax-025" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
