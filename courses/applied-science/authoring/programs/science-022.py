"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def run_cases():
    # Four equally-sized population cells; unequal inclusion is known by design.
    y = np.array([1.0, 2.0, 5.0, 8.0])
    pi = np.array([0.2, 0.4, 0.5, 0.8])
    expected_ht = float(np.sum(pi * y / pi))
    assert expected_ht == y.sum()
    actual_sample = np.array([0, 1, 0, 1], bool)
    ht = float(np.sum(y[actual_sample] / pi[actual_sample]))
    hajek = float(np.sum(y[actual_sample] / pi[actual_sample]) / np.sum(1 / pi[actual_sample]))
    # Cluster design effect derives from covariance, not from a universal penalty.
    cluster_size = 5
    rho = 0.3
    design_effect = 1 + (cluster_size - 1) * rho
    covariance = np.full((cluster_size, cluster_size), rho)
    np.fill_diagonal(covariance, 1)
    assert np.isclose(covariance.sum() / cluster_size, design_effect)
    return dict(
        population_total=float(y.sum()),
        expected_ht=expected_ht,
        sample_ht=ht,
        hajek_mean=hajek,
        design_effect=design_effect,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-022 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
