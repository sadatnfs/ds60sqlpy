"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def run_cases():
    value = np.array([10.0, 8.0, 6.0])
    cost = np.array([6.0, 5.0, 4.0])
    fit = optimize.milp(
        -value,
        integrality=np.ones(3),
        bounds=optimize.Bounds(0, 1),
        constraints=optimize.LinearConstraint(cost, -np.inf, 9),
    )
    assert fit.success and np.allclose(fit.x, [0, 1, 1]) and np.isclose(-fit.fun, 14)
    relaxed = optimize.linprog(-value, A_ub=[cost], b_ub=[9], bounds=[(0, 1)] * 3, method="highs")
    rounded = np.rint(relaxed.x)
    assert relaxed.success and -relaxed.fun > -fit.fun
    assert cost @ rounded > 9
    # Integrality and feasibility are checked separately from a solver status.
    integral = np.allclose(fit.x, np.round(fit.x), atol=1e-7)
    feasible = cost @ fit.x <= 9 + 1e-7
    return dict(
        binary=fit.x.tolist(),
        integer_value=-fit.fun,
        relaxation_bound=-relaxed.fun,
        rounded_cost=float(cost @ rounded),
        integral=bool(integral),
        feasible=bool(feasible),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-017 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
