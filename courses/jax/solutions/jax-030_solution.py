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


def admit(design, targets, mask, penalty):
    if design.ndim != 2 or targets.shape != (design.shape[0],) or mask.shape != targets.shape:
        raise ValueError("row contracts differ")
    if np.asarray(mask).dtype != np.bool_ or not np.asarray(mask).any():
        raise ValueError("nonempty Boolean observation mask required")
    if not math.isfinite(penalty) or penalty < 0:
        raise ValueError("nonnegative finite penalty required")
    if not np.isfinite(np.asarray(design)).all() or not np.isfinite(np.asarray(targets)).all():
        raise ValueError("finite literal data required")


def objective(weight, design, targets, mask, penalty):
    squared = (design @ weight - targets) ** 2
    return jnp.where(mask, squared, 0.0).sum() / mask.sum() + penalty * jnp.vdot(weight, weight)


def solve(design, targets, mask, penalty):
    count = mask.sum()
    weighted = mask[:, None] * design
    matrix = design.T @ weighted / count + penalty * jnp.eye(design.shape[1])
    rhs = design.T @ jnp.where(mask, targets, 0.0) / count
    return jnp.linalg.solve(matrix, rhs)


design = jnp.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
targets = jnp.array([1.0, 3.0, 5.0])
mask = jnp.ones(3, dtype=bool)


def main():
    # Case 1: An independently known solution
    admit(design, targets, mask, 0.0)
    weight = solve(design, targets, mask, 0.0)
    close(weight, [1.0, 2.0])
    close(objective(weight, design, targets, mask, 0.0), 0.0)
    close(jax.grad(objective)(weight, design, targets, mask, 0.0), [0.0, 0.0])

    # Case 2: An ignored outlier is not an observation
    x = jnp.concatenate([design, jnp.array([[100.0, 100.0]])])
    y = jnp.concatenate([targets, jnp.array([-100.0])])
    m = jnp.array([True, True, True, False])
    admit(x, y, m, 0.0)
    close(solve(x, y, m, 0.0), [1.0, 2.0])

    # Case 3: Check a penalty convention
    weight = solve(design, targets, mask, 0.1)
    assert not np.allclose(np.asarray(weight), [1.0, 2.0])
    close(jax.grad(objective)(weight, design, targets, mask, 0.1), [0.0, 0.0])

    # Case 4: Preserve row identity under permutation
    close(solve(design[::-1], targets[::-1], mask[::-1], 0.0), [1.0, 2.0])

    # Case 5: Reject an empty population
    try:
        admit(design, targets, jnp.zeros(3, dtype=bool), 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("empty population admitted")

    # Case 6: Reject an invalid penalty
    try:
        admit(design, targets, mask, -0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative penalty admitted")

    # Case 7: Check transformation parity
    close(jax.jit(solve)(design, targets, mask, 0.1), solve(design, targets, mask, 0.1))

    # Case 8: Transfer the target rule
    close(solve(design, jnp.array([2.0, 5.0, 8.0]), mask, 0.0), [2.0, 3.0])

    print("jax-030" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
