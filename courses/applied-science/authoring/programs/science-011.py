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


def weibull_aft_nll_gradient(theta, time, event, covariate):
    """Weibull AFT model with log scale b0 + b1 * covariate; theta is (log shape, b0, b1)."""
    t, d, x = (np.asarray(value, float) for value in (time, event, covariate))
    shape = np.exp(theta[0])
    log_scale = theta[1] + theta[2] * x
    ratio = np.log(t) - log_scale
    hazard_integral = np.exp(shape * ratio)
    log_hazard = theta[0] - log_scale + (shape - 1) * ratio
    objective = -float(np.sum(d * log_hazard - hazard_integral))
    derivative_shape = -np.sum(d * (1 + shape * ratio) - shape * ratio * hazard_integral)
    # Each log scale enters with derivative shape * (event - cumulative hazard).
    residual = shape * (d - hazard_integral)
    return objective, np.array([derivative_shape, np.sum(residual), np.sum(residual * x)])


def group_scale(time, event, shape):
    """Closed-form Weibull scale MLE for one group at a fixed shape."""
    t, d = np.asarray(time, float), np.asarray(event, float)
    return float((np.sum(t**shape) / np.sum(d)) ** (1 / shape))


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

    # An AFT covariate multiplies the time scale. Every treated duration is twice its
    # control counterpart with the same censoring, so the exact time ratio is 2.
    control = np.array([1.0, 2.0, 3.0, 5.0, 7.0])
    control_event = np.array([1, 1, 0, 1, 0])
    x = np.r_[np.zeros(5), np.ones(5)]
    times, events = np.r_[control, 2 * control], np.r_[control_event, control_event]
    aft = optimize.minimize(
        lambda theta: weibull_aft_nll_gradient(theta, times, events, x),
        np.zeros(3),
        jac=True,
        method="BFGS",
        options={"gtol": 1e-8},
    )
    aft_shape, time_ratio = float(np.exp(aft.x[0])), float(np.exp(aft.x[2]))
    aft_gradient_norm = float(np.linalg.norm(aft.jac))
    assert aft.success and aft_gradient_norm < 1e-5
    assert np.isclose(time_ratio, 2.0, rtol=1e-6)
    assert np.isclose(np.exp(aft.x[1]), group_scale(control, control_event, aft_shape), rtol=1e-6)
    return dict(
        censored_rate=rate,
        naive_rate=naive,
        left_truncated_rate=entered,
        weibull_shape_scale=np.exp(fit.x).tolist(),
        optimizer_success=bool(fit.success),
        optimizer_message=str(fit.message),
        gradient_norm=gradient_norm,
        aft_shape=aft_shape,
        aft_control_scale=float(np.exp(aft.x[1])),
        aft_time_ratio=time_ratio,
        aft_hazard_ratio=time_ratio**-aft_shape,
        aft_gradient_norm=aft_gradient_norm,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-011 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
