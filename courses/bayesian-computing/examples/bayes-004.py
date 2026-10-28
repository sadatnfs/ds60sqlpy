"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


def run_cases():
    z = np.linspace(-12, 12, 40001)
    theta = special.expit(z)
    log_beta = stats.beta.logpdf(theta, 2, 2)
    log_jacobian = -np.logaddexp(0, -z) - np.logaddexp(0, z)
    correct = np.exp(log_beta + log_jacobian)
    wrong = np.exp(log_beta)
    normalizer = float(np.trapezoid(correct, z))
    second_correct = float(np.trapezoid(theta**2 * correct, z) / normalizer)
    second_wrong = float(np.trapezoid(theta**2 * wrong, z) / np.trapezoid(wrong, z))
    assert np.isclose(normalizer, 1, atol=1e-8)
    assert np.isclose(second_correct, 0.3, atol=1e-6) and np.isclose(second_wrong, 1 / 3, atol=3e-5)
    assert second_wrong > second_correct
    return dict(
        transformed_normalizer=normalizer,
        correct_theta_second_moment=second_correct,
        omitted_jacobian_second_moment=second_wrong,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-004 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
