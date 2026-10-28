"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def group_time_effect(outcomes, first_treated, group, time):
    y = np.asarray(outcomes, float)
    g = np.asarray(first_treated)
    if y.ndim != 2 or len(g) != len(y) or not 1 <= group <= time < y.shape[1]:
        raise ValueError("Use a valid pretreatment baseline and observed follow-up time")
    baseline = group - 1
    target = g == group
    controls = g > time
    if not target.any() or not controls.any() or time < group:
        raise ValueError("Need a treated cohort, pretreatment baseline and eligible controls")
    return float(
        (y[target, time] - y[target, baseline]).mean()
        - (y[controls, time] - y[controls, baseline]).mean()
    )


def run_cases():
    g = np.array([2, 2, 4, 4, 99, 99])
    periods = np.arange(6)
    baseline = np.arange(6.0)[:, None] + periods[None, :]
    y = baseline.copy()
    for i, entry in enumerate(g):
        if entry < 99:
            y[i, entry:] += np.arange(1, 7 - entry) * 2
    early = group_time_effect(y, g, 2, 4)
    late = group_time_effect(y, g, 4, 4)
    contaminated = float(
        (y[g == 4, 4] - y[g == 4, 3]).mean() - (y[g == 2, 4] - y[g == 2, 3]).mean()
    )
    assert early == 6 and late == 2 and contaminated == 0
    assert group_time_effect(y, g, 2, 2) == 2
    return dict(
        early_cohort_at_t4=early, late_cohort_at_t4=late, already_treated_comparison=contaminated
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-004 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
