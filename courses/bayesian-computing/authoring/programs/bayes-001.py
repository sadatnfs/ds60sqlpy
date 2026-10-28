"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def posterior(prior, likelihood):
    prior, likelihood = np.asarray(prior, float), np.asarray(likelihood, float)
    if prior.shape != likelihood.shape or np.any(prior < 0) or not np.isclose(prior.sum(), 1):
        raise ValueError("Use matching hypotheses and a normalized prior")
    if (
        not np.all(np.isfinite(likelihood))
        or np.any(likelihood < 0)
        or np.dot(prior, likelihood) <= 0
    ):
        raise ValueError("Evidence needs finite nonnegative likelihood and positive probability")
    mass = prior * likelihood
    return mass / mass.sum()


def run_cases():
    prior = np.array([0.8, 0.2])
    likelihood = np.array([0.1, 0.9])
    one = posterior(prior, likelihood)
    independent_two = posterior(prior, likelihood**2)
    assert np.isclose(one[1], 9 / 13)
    assert np.isclose(independent_two[1], 81 / 85)
    correlated_repeat = one.copy()
    assert correlated_repeat[1] < independent_two[1]
    odds = (prior[1] / prior[0]) * (likelihood[1] / likelihood[0])
    assert np.isclose(odds, one[1] / one[0])
    return dict(
        one_signal=one.tolist(),
        two_independent_signals=independent_two.tolist(),
        perfectly_repeated_signal=correlated_repeat.tolist(),
        posterior_odds=float(odds),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-001 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
