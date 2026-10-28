"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def rank_experiment(repetitions=500, draws=64, shift=0.0, ignore_data=False):
    rng = np.random.default_rng(8)
    theta = rng.normal(size=repetitions)
    y = theta + rng.normal(size=repetitions)
    location = np.zeros(repetitions) if ignore_data else y / 2 + shift
    scale = 1 if ignore_data else np.sqrt(0.5)
    posterior = rng.normal(location[:, None], scale, size=(repetitions, draws))
    rank = np.sum(posterior < theta[:, None], axis=1)
    return rank, posterior.mean(axis=1), y


def run_cases():
    ranks, means, y = rank_experiment()
    biased, _, _ = rank_experiment(shift=1.0)
    prior_ranks, prior_means, _ = rank_experiment(ignore_data=True)
    assert abs(ranks.mean() - 32) < 4 and biased.mean() < ranks.mean() - 10
    assert abs(prior_ranks.mean() - 32) < 4
    conditional_error = float(np.mean((means - y / 2) ** 2))
    ignored_error = float(np.mean((prior_means - y / 2) ** 2))
    assert ignored_error > 5 * conditional_error
    return dict(
        correct_rank_mean=float(ranks.mean()),
        biased_rank_mean=float(biased.mean()),
        prior_only_rank_mean=float(prior_ranks.mean()),
        correct_conditional_error=conditional_error,
        ignored_data_conditional_error=ignored_error,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-008 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
