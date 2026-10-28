"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def policy_ipw_value(records, policy):
    total = 0.0
    for probability, a0, l1, a1, outcome, e0, e1 in records:
        if a0 == policy(0, None) and a1 == policy(1, l1):
            path_prob = (e0 if a0 else 1 - e0) * (e1 if a1 else 1 - e1)
            total += probability * outcome / path_prob
    return total


def run_cases():
    records = []
    for a0 in (0, 1):
        for l1 in (0, 1):
            p_l = 0.2 + 0.4 * a0
            e1 = 0.2 + 0.6 * l1
            for a1 in (0, 1):
                probability = 0.5 * (p_l if l1 else 1 - p_l) * (e1 if a1 else 1 - e1)
                y = 1 + 2 * a0 + 3 * a1 + 2 * l1
                records.append((probability, a0, l1, a1, y, 0.5, e1))
    value = policy_ipw_value(records, lambda time, l: 1)
    assert np.isclose(value, 7.2)
    # A lagged label is not a baseline variable merely because it is in today's warehouse.
    rows = [
        dict(eligible=0, assigned=0, event=2, available=3),
        dict(eligible=0, assigned=1, event=0, available=0),
    ]
    assert not all(row["available"] <= row["assigned"] for row in rows)
    return dict(
        always_treat_value=value,
        probability_total=sum(row[0] for row in records),
        invalid_baseline_rows=1,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-006 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
