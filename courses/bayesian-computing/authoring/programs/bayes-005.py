"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import stats


def run_cases():
    alpha, beta = 10, 4
    benefit, cost = 8.0, 5.0
    threshold = cost / benefit
    mean = alpha / (alpha + beta)
    expected_net = benefit * mean - cost
    positive_probability = float(stats.beta.sf(threshold, alpha, beta))
    assert expected_net > 0 and 0.5 < positive_probability < 1
    theta = np.linspace(0.0001, 0.9999, 20001)
    density = stats.beta.pdf(theta, alpha, beta)
    regret_treat = float(np.trapezoid(np.maximum(cost - benefit * theta, 0) * density, theta))
    regret_wait = float(np.trapezoid(np.maximum(benefit * theta - cost, 0) * density, theta))
    assert regret_treat < regret_wait
    assert np.isclose(regret_wait - regret_treat, expected_net, atol=1e-6)
    return dict(
        expected_net_benefit=expected_net,
        probability_benefit_positive=positive_probability,
        regret_treat=regret_treat,
        regret_wait=regret_wait,
        decision="treat under the stated linear utility",
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-005 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
