"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


def predictive_mass(k, trials, alpha, beta):
    k = np.asarray(k)
    log_choose = (
        special.gammaln(trials + 1) - special.gammaln(k + 1) - special.gammaln(trials - k + 1)
    )
    return np.exp(
        log_choose + special.betaln(alpha + k, beta + trials - k) - special.betaln(alpha, beta)
    )


def run_cases():
    a, b = 2 + 8, 2 + 2
    future = 5
    k = np.arange(future + 1)
    probabilities = predictive_mass(k, future, a, b)
    mean = float(k @ probabilities)
    variance = float(((k - mean) ** 2) @ probabilities)
    plugin = future * (a / (a + b)) * (b / (a + b))
    assert (
        np.isclose(probabilities.sum(), 1)
        and np.isclose(mean, future * a / (a + b))
        and variance > plugin
    )
    duplicated_variance = stats.beta.var(18, 6)
    correct_variance = stats.beta.var(a, b)
    assert duplicated_variance < correct_variance
    return dict(
        posterior_mean=a / (a + b),
        future_probabilities=probabilities.tolist(),
        predictive_variance=variance,
        plug_in_variance=plugin,
        correct_parameter_variance=float(correct_variance),
        duplicated_record_variance=float(duplicated_variance),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-003 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
