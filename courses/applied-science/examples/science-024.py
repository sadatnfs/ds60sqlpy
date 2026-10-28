"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def run_cases():
    # Reproducible capstone ledger: effects, uncertainty and finite resource decisions.
    regions = ["north", "south", "east"]
    control = np.array([[-1.0, 0.0, 0.0, 1.0], [-2.0, 0.0, 0.0, 2.0], [-0.5, 0.0, 0.0, 0.5]])
    treated = control + np.array([3.0, 1.0, -1.0])[:, None]
    effects = treated.mean(axis=1) - control.mean(axis=1)
    se = np.sqrt(treated.var(axis=1, ddof=1) / 4 + control.var(axis=1, ddof=1) / 4)
    assert np.allclose(effects, [3, 1, -1])
    assert np.allclose(se, np.sqrt([1 / 3, 4 / 3, 1 / 12]))
    cost = np.array([3.0, 2.0, 1.0])
    lower = effects - 1.96 * se
    fit = optimize.milp(
        -lower,
        integrality=np.ones(3),
        bounds=optimize.Bounds(0, 1),
        constraints=optimize.LinearConstraint(cost, -np.inf, 4),
    )
    assert fit.success and np.allclose(fit.x, [1, 0, 0])
    selected = [name for name, chosen in zip(regions, fit.x, strict=True) if chosen > 0.5]
    assert selected == ["north"]
    revised = np.array([0.1, 1.0, -1.0])
    new_lower = revised - 1.96 * se
    updated = optimize.milp(
        -new_lower,
        integrality=np.ones(3),
        bounds=optimize.Bounds(0, 1),
        constraints=optimize.LinearConstraint(cost, -np.inf, 4),
    )
    assert updated.success and updated.x.sum() == 0
    ledger = dict(
        estimand="region-specific additive effect under stated assignment",
        cutoff=10,
        budget=4,
        objective="sum of marginal lower bounds",
        selected=selected,
        rollback_after_revision=True,
    )
    # A sum of marginal lower bounds is a conservative utility score, not a joint95% bound.
    return dict(
        ledger=ledger,
        lower_bounds=lower.tolist(),
        estimated_effects=effects.tolist(),
        standard_errors=se.tolist(),
        selected_cost=float(cost @ fit.x),
        updated_selection_count=int(updated.x.sum()),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-024 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
