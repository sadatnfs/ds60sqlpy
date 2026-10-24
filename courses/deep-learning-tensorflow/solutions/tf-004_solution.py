from __future__ import annotations

import numpy as np


def reduce_squared(residuals, reduction="mean", mask=None):
    residuals = np.asarray(residuals, dtype=np.float64)
    if residuals.ndim != 1 or residuals.size == 0 or not np.isfinite(residuals).all():
        raise ValueError("finite nonempty residual vector required")
    if reduction not in {"mean", "sum"}:
        raise ValueError("reduction must be mean or sum")
    if mask is not None:
        mask = np.asarray(mask)
        if mask.dtype != np.bool_:
            raise TypeError("mask must be boolean")
        if mask.shape != residuals.shape or not mask.any():
            raise ValueError("same-shaped nonempty mask required")
        residuals = residuals[mask]
    squared = np.square(residuals)
    return float(squared.mean() if reduction == "mean" else squared.sum())


def verify():
    # Exercise 1: loss units and reductions
    assert reduce_squared([1, -1, 2], "sum") == 6 and reduce_squared([1, -1, 2]) == 2
    # Exercise 2: duplicate observations
    assert reduce_squared([1, -1, 2] * 2, "sum") == 12 and reduce_squared([1, -1, 2] * 2) == 2
    # Exercise 3: selected denominator
    assert reduce_squared([1, -1, 2], mask=[True, True, False]) == 1
    # Exercise 4: invalid objectives
    for error, values, reduction, mask in (
        (ValueError, [], "mean", None),
        (ValueError, [1], "mean", [False]),
        (TypeError, [1], "mean", [1]),
        (ValueError, [1], "median", None),
    ):
        try:
            reduce_squared(values, reduction, mask)
        except error:
            pass
        else:
            raise AssertionError("invalid objective accepted")
    # Exercise 5: different metric rankings
    assert reduce_squared([0, 0, 4]) > reduce_squared([2, 2, 2])
    assert np.abs([0, 0, 4]).mean() < np.abs([2, 2, 2]).mean()
    # Exercise 6: group versus example weighting
    assert (
        reduce_squared([2, 0, 0, 0]) == 1
        and (reduce_squared([2]) + reduce_squared([0, 0, 0])) / 2 == 2
    )
    return {"sum": 6, "mean": 2, "masked_mean": 1}


if __name__ == "__main__":
    print(verify())
