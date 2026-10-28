"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def solve_mix(capacity):
    return optimize.linprog(
        [-3.0, -2.0],
        A_ub=[[1, 1], [2, 1]],
        b_ub=[capacity, 8],
        bounds=[(0, None)] * 2,
        method="highs",
    )


def run_cases():
    fit = solve_mix(5)
    assert fit.success and np.allclose(fit.x, [3, 2]) and np.isclose(-fit.fun, 13)
    epsilon = 0.001
    near = solve_mix(5 + epsilon)
    value_derivative = (-near.fun + fit.fun) / epsilon
    shadow = -float(fit.ineqlin.marginals[0])
    assert np.isclose(value_derivative, shadow) and shadow == 1
    far = solve_mix(9)
    assert not np.isclose(-far.fun, 13 + 4 * shadow)
    assert np.all(np.asarray([[1, 1], [2, 1]]) @ fit.x <= np.array([5, 8]) + 1e-8)
    return dict(
        allocation=fit.x.tolist(),
        value=-fit.fun,
        local_shadow_price=shadow,
        large_change_value=-far.fun,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-016 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
