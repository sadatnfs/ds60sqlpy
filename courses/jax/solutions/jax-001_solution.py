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


def predict(weight, inputs):
    return weight * inputs


def mse(weight, inputs, targets):
    if inputs.ndim != 1 or inputs.shape != targets.shape or inputs.size == 0:
        raise ValueError("one nonempty target per input")
    return jnp.mean((predict(weight, inputs) - targets) ** 2)


x = jnp.array([1.0, 2.0, 3.0])
y = 2 * x


def main():
    # Case 1: A hand-calculated loss
    close(predict(0.0, x), [0.0, 0.0, 0.0])
    close(mse(0.0, x, y), 56 / 3)

    # Case 2: A plausible shape mistake
    try:
        mse(0.0, x, y[:, None])
    except ValueError:
        pass
    else:
        raise AssertionError("shape mismatch accepted")

    # Case 3: Trace another predictor
    close(predict(1.0, x), [1.0, 2.0, 3.0])
    close(mse(1.0, x, y), 14 / 3)

    # Case 4: Construct an exact fit
    close(mse(2.0, x, y), 0.0)

    # Case 5: Change the target
    close(mse(2.0, x, jnp.array([2.0, 4.0, 7.0])), 1 / 3)

    # Case 6: Reject missing observations
    try:
        mse(0.0, jnp.array([]), jnp.array([]))
    except ValueError:
        pass
    else:
        raise AssertionError("empty loss accepted")

    # Case 7: Separate sum from mean
    close(jnp.sum((0.0 * x - y) ** 2), 56.0)
    close(3 * mse(0.0, x, y), 56.0)

    # Case 8: Transfer to new inputs
    close(predict(2.0, jnp.array([4.0, 5.0])), [8.0, 10.0])

    print("jax-001" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
