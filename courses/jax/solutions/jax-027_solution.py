"""Small offline JAX mechanism investigation; CPU evidence only."""

from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp

from jax.sharding import Mesh, NamedSharding, PartitionSpec

# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)


mesh = Mesh(np.asarray(jax.devices("cpu")[:1]), ("data",))
row_layout = NamedSharding(mesh, PartitionSpec("data", None))
replicated = NamedSharding(mesh, PartitionSpec())
host = np.arange(6.0, dtype=np.float64).reshape(3, 2)


def main():
    # Case 1: Place and inspect a real array
    placed = jax.device_put(host, row_layout)
    assert placed.shape == (3, 2)
    assert len(placed.addressable_shards) == 1
    assert placed.addressable_shards[0].device.platform == "cpu"
    close(placed.addressable_shards[0].data, host)

    # Case 2: Specify output placement
    placed = jax.device_put(host, row_layout)
    function = jax.jit(lambda x: x.T @ x, in_shardings=row_layout, out_shardings=replicated)
    result = function(placed)
    close(result, host.T @ host)
    assert result.sharding.is_equivalent_to(replicated, result.ndim)

    # Case 3: Inspect mesh identity
    assert mesh.shape["data"] == 1
    assert all(device.platform == "cpu" for device in mesh.devices.flat)

    # Case 4: Round-trip values
    placed = jax.device_put(host, row_layout)
    assert placed.is_fully_addressable
    close(np.asarray(placed), host)

    # Case 5: Inspect the specification
    assert row_layout.spec == PartitionSpec("data", None)
    assert replicated.spec == PartitionSpec()

    # Case 6: Differentiate a placed calculation
    placed = jax.device_put(host, row_layout)
    close(jax.grad(lambda x: jnp.sum(x * x))(placed), 2 * host)

    # Case 7: Change the row count
    other = np.arange(10.0, dtype=np.float64).reshape(5, 2)
    placed = jax.device_put(other, row_layout)
    assert placed.shape == (5, 2)
    close(placed.addressable_shards[0].data, other)

    # Case 8: State the evidence limit
    placed = jax.device_put(host, row_layout)
    assert len(placed.devices()) == 1

    print("jax-027" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
