"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize, special


def cox_loglik(beta, time, event, x, entry=None):
    time, event, x = np.asarray(time), np.asarray(event), np.asarray(x, float)
    entry = np.zeros(len(time)) if entry is None else np.asarray(entry)
    total = 0.0
    for i in np.flatnonzero(event):
        risk = (entry <= time[i]) & (time >= time[i])
        total += beta * x[i] - special.logsumexp(beta * x[risk])
    return float(total)


def run_cases():
    t = np.array([1.0, 2.0, 3.0, 4.0])
    d = np.array([1, 1, 0, 1])
    x = np.array([1.0, 0.0, 1.0, 0.0])
    zero = cox_loglik(0, t, d, x)
    assert np.isclose(zero, -np.log(4) - np.log(3))
    entry = np.array([0.0, 0.0, 2.5, 0.0])
    delayed = cox_loglik(0, t, d, x, entry)
    assert np.isclose(delayed, -np.log(3) - np.log(2))
    grid = np.linspace(-2, 2, 401)
    scores = np.array([cox_loglik(b, t, d, x) for b in grid])
    best = float(grid[scores.argmax()])
    assert scores.max() >= zero
    fit = optimize.minimize_scalar(
        lambda b: -cox_loglik(b, t, d, x), bounds=(-3, 3), method="bounded"
    )
    assert fit.success and np.isclose(fit.x, 0.5 * np.log(2), atol=1e-5)
    return dict(
        zero_log_partial_likelihood=zero,
        delayed_entry_log_partial_likelihood=delayed,
        grid_beta=best,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-010 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
