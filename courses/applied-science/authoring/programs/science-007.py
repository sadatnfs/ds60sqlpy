"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def as_of(records, cutoff):
    eligible = [r for r in records if r[1] <= cutoff]
    latest = {}
    for event, available, value in sorted(eligible, key=lambda r: (r[0], r[1])):
        latest[event] = value
    return latest


def run_cases():
    records = [(0, 1, 10.0), (1, 2, 12.0), (2, 8, 50.0), (2, 3, 14.0), (3, 4, 16.0), (4, 5, 18.0)]
    old = as_of(records, 4)
    current = as_of(records, 9)
    assert old[2] == 14 and current[2] == 50

    def extrapolate(values):
        t = np.array(sorted(values))
        y = np.array([values[k] for k in t])
        return float(np.polyval(np.polyfit(t, y, 1), 4))

    vintage = extrapolate(old)
    leaked = extrapolate({k: v for k, v in current.items() if k <= 3})
    assert np.isclose(vintage, 18) and not np.isclose(leaked, 18)
    # Overlapping two-step forecasts reuse a target and must not be iid resampled.
    targets = [(origin, horizon, origin + horizon) for origin in (2, 3) for horizon in (1, 2)]
    assert len({r[2] for r in targets}) < len(targets)
    return dict(
        vintage_forecast=vintage,
        revised_backtest=leaked,
        unique_targets=len({r[2] for r in targets}),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-007 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
