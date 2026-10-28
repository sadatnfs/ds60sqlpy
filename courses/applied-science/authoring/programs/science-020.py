"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def gls_mean(effect, covariance):
    y = np.asarray(effect, float)
    v = np.asarray(covariance, float)
    if v.shape != (len(y), len(y)) or not np.all(np.isfinite(v)) or not np.allclose(v, v.T):
        raise ValueError("Covariance must be finite, square and symmetric")
    try:
        np.linalg.cholesky(v)
    except np.linalg.LinAlgError as error:
        raise ValueError("Covariance must be positive definite") from error
    one = np.ones(len(y))
    solve = np.linalg.solve(v, one)
    return float(solve @ y / (one @ solve)), float(1 / (one @ solve))


def run_cases():
    y = np.array([0.4, 0.6])
    independent = np.diag([0.04, 0.04])
    dependent = np.array([[0.04, 0.03], [0.03, 0.04]])
    naive = gls_mean(y, independent)
    aware = gls_mean(y, dependent)
    assert (
        naive[0] == aware[0] == 0.5 and np.isclose(naive[1], 0.02) and np.isclose(aware[1], 0.035)
    )
    visible = np.array([0.3, 0.5, 0.7])
    with_missing = np.r_[visible, [-0.2, -0.1]]
    assert with_missing.mean() < visible.mean()
    # The added effects are a stated scenario, not estimated unpublished truth.
    return dict(
        independent_variance=naive[1],
        dependent_variance=aware[1],
        published_mean=float(visible.mean()),
        sensitivity_mean=float(with_missing.mean()),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-020 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
