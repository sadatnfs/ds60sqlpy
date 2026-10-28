"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


def normalized_log_weights(log_weights):
    x = np.asarray(log_weights, float)
    if (
        x.ndim != 1
        or not len(x)
        or np.any(np.isnan(x))
        or np.any(np.isposinf(x))
        or not np.any(np.isfinite(x))
    ):
        raise ValueError(
            "Use finite or negative-infinite log weights with at least one finite value"
        )
    return np.exp(x - special.logsumexp(x))


def run_cases():
    grid = np.linspace(-6, 6, 40001)
    y = np.array([1.0, 2.0, 3.0])
    logp = stats.norm.logpdf(grid, 0, 2) + stats.norm.logpdf(y[:, None], grid[None, :], 1).sum(
        axis=0
    )
    mass = normalized_log_weights(logp)
    mean = float(grid @ mass)
    variance = float(((grid - mean) ** 2) @ mass)
    assert np.isclose(mean, 24 / 13, atol=1e-6) and np.isclose(variance, 4 / 13, atol=1e-6)
    far = np.array([-45000.0, -45001.0, -45002.0])
    stable = normalized_log_weights(far)
    assert np.exp(far).sum() == 0 and np.isclose(stable.sum(), 1)
    assert np.allclose(stable, normalized_log_weights(far + 45000))
    return dict(
        grid_mean=mean,
        analytic_mean=24 / 13,
        grid_variance=variance,
        analytic_variance=4 / 13,
        stable_extreme_weights=stable.tolist(),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-002 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
