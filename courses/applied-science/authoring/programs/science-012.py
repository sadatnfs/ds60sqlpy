"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def competing_incidence(time, cause):
    t, c = np.asarray(time), np.asarray(cause)
    survival = 1.0
    incidence = np.zeros(2)
    for value in np.unique(t):
        risk = int(np.sum(t >= value))
        events = np.array([np.sum((t == value) & (c == k)) for k in (1, 2)])
        incidence += survival * events / risk
        survival *= 1 - events.sum() / risk
    return incidence, survival


def run_cases():
    incidence, survival = competing_incidence([1, 2, 3, 4], [1, 2, 1, 2])
    assert np.allclose(incidence, [0.5, 0.5]) and survival == 0
    # Censoring the competing cause estimates a different hypothetical quantity.
    km = 1.0
    for i, cause in enumerate([1, 2, 1, 2]):
        if cause == 1:
            km *= 1 - 1 / (4 - i)
    naive = 1 - km
    assert naive > 0.5
    ph_residuals = np.array([1.0, 0.8, 0.4, -0.2, -0.8, -1.0])
    trend = float(np.corrcoef(np.arange(6), ph_residuals)[0, 1])
    assert trend < -0.95
    return dict(
        cause_incidence=incidence.tolist(), naive_one_minus_km=naive, schoenfeld_style_trend=trend
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-012 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
