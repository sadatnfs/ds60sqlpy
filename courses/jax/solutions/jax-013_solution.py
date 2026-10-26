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


def admit(logits, targets, active):
    labels, mask = np.asarray(targets), np.asarray(active)
    if logits.ndim != 2 or labels.shape != (logits.shape[0],) or mask.shape != labels.shape:
        raise ValueError("one target and mask per logit row")
    if mask.dtype != np.bool_ or not mask.any():
        raise ValueError("at least one active Boolean target")
    if np.any(labels[mask] < 0) or np.any(labels[mask] >= logits.shape[1]):
        raise ValueError("active target outside classes")


def token_mean(logits, targets, active):
    safe = jnp.where(active, targets, 0)
    selected = jnp.take_along_axis(jax.nn.log_softmax(logits), safe[:, None], axis=1)[:, 0]
    return -jnp.where(active, selected, 0.0).sum() / active.sum()


logits = jnp.zeros((4, 3))
targets = jnp.array([0, 1, 2, -100])
active = jnp.array([True, True, True, False])


def main():
    # Case 1: Uniform active-target accounting
    admit(logits, targets, active)
    assert int(active.sum()) == 3
    close(token_mean(logits, targets, active), math.log(3.0))

    # Case 2: Inspect direct gradients
    g = jax.grad(token_mean)(logits, targets, active)
    expected = np.full((4, 3), 1 / 9)
    expected[np.arange(3), np.arange(3)] = -2 / 9
    expected[3] = 0.0
    close(g, expected)

    # Case 3: Append ignored storage
    padded = jnp.zeros((6, 3))
    labels = jnp.array([0, 1, 2, -100, -100, -100])
    mask = jnp.array([True, True, True, False, False, False])
    admit(padded, labels, mask)
    close(token_mean(padded, labels, mask), math.log(3.0))

    # Case 4: Reject an empty objective
    try:
        admit(logits, targets, jnp.zeros(4, dtype=bool))
    except ValueError:
        pass
    else:
        raise AssertionError("empty supervision accepted")

    # Case 5: Check target identity
    scores = jnp.array([[math.log(3.0), 0.0]])
    mask = jnp.array([True])
    close(token_mean(scores, jnp.array([0]), mask), math.log(4 / 3))
    close(token_mean(scores, jnp.array([1]), mask), math.log(4.0))

    # Case 6: Keep an extreme logit finite
    value = token_mean(jnp.array([[1000.0, 0.0, -1000.0]]), jnp.array([0]), jnp.array([True]))
    assert bool(jnp.isfinite(value))
    close(value, 0.0)

    # Case 7: Reject an active sentinel
    try:
        admit(logits, targets, jnp.ones(4, dtype=bool))
    except ValueError:
        pass
    else:
        raise AssertionError("active sentinel accepted")

    # Case 8: Compile the admitted calculation
    admit(logits, targets, active)
    close(jax.jit(token_mean)(logits, targets, active), math.log(3.0))

    print("jax-013" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
