"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def inventory_loss(quantity, demand, under=4.0, over=1.0):
    d = np.asarray(demand, float)
    return under * np.maximum(d - quantity, 0) + over * np.maximum(quantity - d, 0)


def run_cases():
    demand = np.array([2.0, 3.0, 4.0, 12.0])
    prob = np.array([0.4, 0.3, 0.2, 0.1])
    quantities = np.arange(13.0)
    costs = np.array([inventory_loss(q, demand) for q in quantities])
    mean = costs @ prob
    mean_choice = int(quantities[mean.argmin()])
    worst = costs.max(axis=1)
    robust_choice = int(quantities[worst.argmin()])
    assert mean_choice == 4 and robust_choice == 10
    # Perfect-information value compares optimization before vs after observing demand.
    evpi = float(mean.min() - np.sum(prob * np.min(costs, axis=0)))
    assert evpi >= 0
    assert worst[robust_choice] < worst[mean_choice]
    return dict(
        expected_cost_choice=mean_choice,
        minimax_choice=robust_choice,
        expected_cost=float(mean.min()),
        evpi=evpi,
        worst_cost=float(worst[robust_choice]),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-018 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
