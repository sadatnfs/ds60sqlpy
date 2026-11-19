"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
import statsmodels.api as sm


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


def episode_split_cox(time, covariate, split=1.0):
    """Fit a Cox model whose covariate effect may change after `split`.

    Each unit contributes an episode (0, min(t, split)] and, if it survives past
    `split`, a delayed-entry episode (split, t]. The second column is the covariate
    times an after-split indicator, so its coefficient is the change in log hazard
    ratio between the two periods. Every unit in this fixture has an observed event.
    """
    t, x = np.asarray(time, float), np.asarray(covariate, float)
    after = t > split
    stop = np.r_[np.minimum(t, split), t[after]]
    entry = np.r_[np.zeros(len(t)), np.full(after.sum(), split)]
    status = np.r_[(t <= split).astype(float), np.ones(after.sum())]
    period = np.r_[np.zeros(len(t)), np.ones(after.sum())]
    xs = np.r_[x, x[after]]
    design = np.column_stack([xs, xs * period])
    return sm.PHReg(stop, design, status=status, entry=entry).fit()


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

    # Simulate a covariate whose log hazard ratio is +1 before time 1 and -1 after it,
    # by inverting the piecewise-constant cumulative hazard of each unit.
    rng = np.random.default_rng(12)
    n = 400
    x = rng.integers(0, 2, n).astype(float)
    u = rng.exponential(size=n)
    early, late = np.exp(1.0 * x), np.exp(-1.0 * x)
    t = np.where(u < early, u / early, 1 + (u - early) / late)
    constant = sm.PHReg(t, x[:, None], status=np.ones(n)).fit()
    split = episode_split_cox(t, x)
    early_log_hr, change = (float(value) for value in split.params)
    change_se = float(split.bse[1])
    # One constant coefficient averages two opposite effects; the interaction separates them.
    assert 0 < constant.params[0] < early_log_hr
    assert change < 0 and abs(change / change_se) > 3
    return dict(
        cause_incidence=incidence.tolist(),
        naive_one_minus_km=naive,
        constant_log_hazard_ratio=float(constant.params[0]),
        early_log_hazard_ratio=early_log_hr,
        late_log_hazard_ratio=early_log_hr + change,
        time_interaction=change,
        time_interaction_se=change_se,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-012 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
