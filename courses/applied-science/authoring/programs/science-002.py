"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def weighted_effect(outcome, treatment, propensity):
    y, a, e = map(lambda v: np.asarray(v, float), (outcome, treatment, propensity))
    if y.ndim != 1 or y.shape != a.shape or y.shape != e.shape or not len(y):
        raise ValueError("Outcome, treatment and propensity need matching nonempty vectors")
    if not all(np.all(np.isfinite(v)) for v in (y, a, e)) or np.any((a != 0) & (a != 1)):
        raise ValueError("Use finite outcomes, probabilities and binary treatment")
    if np.any((e <= 0) | (e >= 1)):
        raise ValueError("Both treatment possibilities must have positive probability")
    return float(np.mean(a * y / e - (1 - a) * y / (1 - e)))


def effective_n(weights):
    w = np.asarray(weights, float)
    if w.ndim != 1 or not len(w) or not np.all(np.isfinite(w)) or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("Effective size needs finite nonnegative weights and positive total")
    return float(w.sum() ** 2 / (w @ w))


def run_cases():
    # Exact population table: four treatment/covariate cells, replicated by probabilities.
    x = np.repeat([0, 0, 1, 1], [40, 10, 10, 40])
    a = np.repeat([0, 1, 0, 1], [40, 10, 10, 40])
    e = np.where(x == 0, 0.2, 0.8)
    y = 1 + 4 * x + 2 * a
    estimate = weighted_effect(y, a, e)
    weights = np.where(a == 1, 1 / e, 1 / (1 - e))
    assert np.isclose(estimate, 2)
    assert effective_n([1, 1, 1, 50]) < 2
    overlap = e * (1 - e)
    effect_by_x = np.array([4.0, 1.0])
    population = np.array([0.8, 0.2])
    prop = np.array([0.1, 0.6])
    target_weights = population * prop * (1 - prop)
    target_weights /= target_weights.sum()
    overlap_effect = float(target_weights @ effect_by_x)
    population_effect = float(population @ effect_by_x)
    assert not np.isclose(overlap_effect, population_effect)
    return dict(
        ate=estimate,
        weighted_ess=effective_n(weights),
        overlap_effect=overlap_effect,
        population_effect=population_effect,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-002 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
