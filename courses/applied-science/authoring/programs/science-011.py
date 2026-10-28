"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def exponential_mle(time, event, entry=None):
    t, d = np.asarray(time, float), np.asarray(event, int)
    e = np.zeros_like(t) if entry is None else np.asarray(entry, float)
    if np.any(e >= t) or np.sum(d) == 0:
        raise ValueError("Need positive observed durations and an event")
    return float(np.sum(d) / np.sum(t - e))


def weibull_nll_gradient(theta, time, event):
    t, d = np.asarray(time, float), np.asarray(event, float)
    shape, scale = np.exp(theta)
    ratio = np.log(t) - np.log(scale)
    hazard_integral = np.exp(shape * ratio)
    log_hazard = np.log(shape) - np.log(scale) + (shape - 1) * ratio
    objective = -float(np.sum(d * log_hazard - hazard_integral))
    derivative_shape = -np.sum(d * (1 + shape * ratio) - shape * ratio * hazard_integral)
    derivative_scale = shape * np.sum(d - hazard_integral)
    return objective, np.array([derivative_shape, derivative_scale])


def run_cases():
    t = np.array([1.0, 2.0, 4.0, 5.0, 8.0])
    d = np.array([1, 1, 0, 1, 0])
    rate = exponential_mle(t, d)
    naive = 1 / t.mean()
    assert np.isclose(rate, 0.15) and np.isclose(naive, 0.25)
    entered = exponential_mle(t, d, [0, 0, 1, 2, 3])
    assert entered > rate

    # A Weibull log likelihood includes survival contributions for censored units.
    initial = np.log([1.0, 1 / rate])
    fit = optimize.minimize(
        lambda theta: weibull_nll_gradient(theta, t, d),
        initial,
        jac=True,
        method="BFGS",
        options={"gtol": 1e-7},
    )
    gradient_norm = float(np.linalg.norm(fit.jac))
    assert fit.success and gradient_norm < 1e-5
    assert fit.fun <= weibull_nll_gradient(initial, t, d)[0] + 1e-7
    return dict(
        censored_rate=rate,
        naive_rate=naive,
        left_truncated_rate=entered,
        weibull_shape_scale=np.exp(fit.x).tolist(),
        optimizer_success=bool(fit.success),
        optimizer_message=str(fit.message),
        gradient_norm=gradient_norm,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-011 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
