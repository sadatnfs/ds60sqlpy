"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def ridge_predict(x, y, test, penalty):
    x, y, test = np.asarray(x, float), np.asarray(y, float), np.asarray(test, float)
    return test @ np.linalg.solve(x.T @ x + penalty * np.eye(x.shape[1]), x.T @ y)


def run_cases():
    rng = np.random.default_rng(23)
    x = rng.normal(size=(20, 40))
    beta = np.r_[np.ones(3), np.zeros(37)]
    y = x @ beta + rng.normal(scale=0.5, size=20)
    test = rng.normal(size=(50, 40))
    truth = test @ beta
    min_norm = np.linalg.lstsq(x, y, rcond=None)[0]
    train_error = float(np.mean((x @ min_norm - y) ** 2))
    assert train_error < 1e-20
    prediction = ridge_predict(x, y, test, 3.0)
    test_error = float(np.mean((prediction - truth) ** 2))
    assert test_error > 0.01
    # Perfectly duplicated variables do not identify their separate coefficients.
    design = np.c_[np.arange(5.0), np.arange(5.0)]
    assert np.linalg.matrix_rank(design) == 1 and np.allclose(design @ [1, 2], design @ [2, 1])
    return dict(
        interpolating_train_error=train_error, ridge_test_error=test_error, rank_deficient_design=1
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-023 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
