"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def standardize(values, weights):
    values, weights = np.asarray(values, float), np.asarray(weights, float)
    if (
        values.ndim != 1
        or len(values) == 0
        or not np.all(np.isfinite(values))
        or not np.all(np.isfinite(weights))
    ):
        raise ValueError("Use finite nonempty one-dimensional values and weights")
    if values.shape != weights.shape or np.any(weights < 0) or not np.isclose(weights.sum(), 1):
        raise ValueError("Use one nonnegative target distribution with total one")
    return float(values @ weights)


def run_cases():
    m0, m1 = np.array([1.0, 5.0]), np.array([3.0, 6.0])
    trial, target = np.array([0.8, 0.2]), np.array([0.2, 0.8])
    trial_ate = standardize(m1 - m0, trial)
    target_ate = standardize(m1 - m0, target)
    observed_treated = standardize(m1, [0.9, 0.1])
    observed_control = standardize(m0, [0.1, 0.9])
    crude = observed_treated - observed_control
    assert np.isclose(trial_ate, 1.8) and np.isclose(target_ate, 1.2)
    assert crude < 0 < target_ate
    shifted = standardize(m1 + 2 - (m0 + 2), target)
    assert shifted == target_ate
    return dict(trial_ate=trial_ate, target_ate=target_ate, crude_difference=crude)


if __name__ == "__main__":
    evidence = run_cases()
    print("science-001 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
