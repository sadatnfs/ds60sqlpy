"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def sequential_value(policy):
    total = 0.0
    # L1 is affected by A0; enumerating its treatment-specific distribution is essential.
    for l0 in (0, 1):
        a0 = policy(0, l0, None)
        p_l1 = 0.2 + 0.3 * l0 + 0.2 * a0
        for l1 in (0, 1):
            a1 = policy(1, l0, l1)
            prob = 0.5 * (p_l1 if l1 else 1 - p_l1)
            outcome = 1 + 2 * a0 + 3 * a1 + l0 + 2 * l1
            total += prob * outcome
    return total


def run_cases():
    none = sequential_value(lambda t, l0, l1: 0)
    all_ = sequential_value(lambda t, l0, l1: 1)
    dynamic = sequential_value(lambda t, l0, l1: l0 if t == 0 else l1)
    assert np.isclose(none, 2.2) and np.isclose(all_, 7.6)
    assert none < dynamic < all_
    # Holding the mediator at its untreated distribution loses part of the total effect.
    controlled_distribution = none + 5
    assert np.isclose(all_ - controlled_distribution, 0.4)
    return dict(never_treat=none, always_treat=all_, dynamic_policy=dynamic, mediator_path=0.4)


if __name__ == "__main__":
    evidence = run_cases()
    print("science-005 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
