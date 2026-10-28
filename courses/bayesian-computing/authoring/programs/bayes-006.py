"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def metropolis(step, iterations=3000, seed=6):
    rng = np.random.default_rng(seed)
    current = 0.0
    values = []
    accepted = 0
    for _ in range(iterations):
        proposal = current + rng.normal(scale=step)
        if np.log(rng.uniform()) < min(0.0, -0.5 * (proposal**2 - current**2)):
            current = proposal
            accepted += 1
        values.append(current)
    return np.asarray(values[500:]), accepted / iterations


def run_cases():
    chain, acceptance = metropolis(1.0)
    lag = float(np.corrcoef(chain[:-1], chain[1:])[0, 1])
    ar1_ess = len(chain) * (1 - lag) / (1 + lag)
    stuck, stuck_acceptance = metropolis(0.0)
    assert abs(chain.mean()) < 0.2 and 0.7 < chain.var() < 1.3
    assert stuck.mean() == 0 and stuck.var() == 0 and stuck_acceptance == 1
    assert 0 < ar1_ess < len(chain)
    return dict(
        mean=float(chain.mean()),
        variance=float(chain.var()),
        acceptance=acceptance,
        lag_one=lag,
        ar1_approximate_ess=float(ar1_ess),
        stuck_acceptance=stuck_acceptance,
        stuck_variance=float(stuck.var()),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-006 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
