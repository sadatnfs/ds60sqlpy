"""Reference implementation and exact boundary checks for python-numpy-04."""

import math
from collections.abc import Callable

import numpy as np


def logsumexp(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or np.isnan(x).any() or np.isposinf(x).any():
        raise ValueError("Expected finite or negative-infinite log weights")
    if x.size == 0 or np.isneginf(x).all():
        return -math.inf
    maximum = float(x.max())
    with np.errstate(over="ignore"):
        shifted = x - maximum
    return maximum + math.log(float(np.exp(shifted).sum()))


def softmax(scores: np.ndarray) -> np.ndarray:
    x = np.asarray(scores, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.isfinite(x).all():
        raise ValueError("Expected a nonempty finite score vector")
    with np.errstate(over="ignore"):
        weight = np.exp(x - x.max())
    return np.asarray(weight / weight.sum())


def accurate_sum(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all():
        raise ValueError("Expected finite summands")
    try:
        return math.fsum(float(value) for value in x)
    except OverflowError as error:
        raise ValueError("The sum exceeds floating-point range") from error


def floating_dot(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if (
        a.ndim != 1
        or b.ndim != 1
        or a.shape != b.shape
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
    ):
        raise ValueError("Expected equal finite vectors")
    with np.errstate(over="ignore", invalid="ignore"):
        result = float(np.dot(a, b))
    if not math.isfinite(result):
        raise ValueError("Dot product exceeds finite floating range")
    return result


def solve_checked(
    matrix: np.ndarray, target: np.ndarray, max_condition: float = 1e10
) -> np.ndarray:
    a = np.asarray(matrix, dtype=float)
    b = np.asarray(target, dtype=float)
    if (
        a.ndim != 2
        or a.shape[0] == 0
        or a.shape[0] != a.shape[1]
        or b.shape != (a.shape[0],)
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
        or not math.isfinite(max_condition)
        or max_condition < 1
    ):
        raise ValueError("Expected a finite square system and valid condition limit")
    condition = float(np.linalg.cond(a))
    if not math.isfinite(condition) or condition > max_condition:
        raise ValueError("System is singular or exceeds the condition policy")
    return np.asarray(np.linalg.solve(a, b))


def within_tolerance(actual: np.ndarray, expected: np.ndarray, atol: float, rtol: float) -> bool:
    a = np.asarray(actual, dtype=float)
    b = np.asarray(expected, dtype=float)
    if (
        a.shape != b.shape
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
        or not math.isfinite(atol)
        or not math.isfinite(rtol)
        or atol < 0
        or rtol < 0
    ):
        raise ValueError("Expected equal finite shapes and nonnegative tolerances")
    scale = np.maximum(np.abs(a), np.abs(b))
    safe_scale = np.where(scale == 0, 1.0, scale)
    with np.errstate(over="ignore", under="ignore"):
        distance = np.abs(a / safe_scale - b / safe_scale)
        allowance = atol / safe_scale + rtol * (np.abs(b) / safe_scale)
    return bool(np.all(distance <= allowance))


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Aggregate log weights without overflow
    assert math.isclose(logsumexp(np.array([1000.0, 1000.0])), 1000 + math.log(2))
    assert logsumexp(np.array([-np.inf, -np.inf])) == -np.inf
    assert logsumexp(np.array([])) == -np.inf
    expect_value_error(lambda: logsumexp(np.array([np.nan])))
    expect_value_error(lambda: logsumexp(np.array([np.inf])))
    # Exercise 2: Normalize large scores
    s = np.array([1000.0, 1001.0])
    p = softmax(s)
    assert np.isfinite(p).all() and np.isclose(p.sum(), 1) and p[1] > p[0]
    assert np.allclose(p, softmax(s - 1000)) and np.allclose(
        softmax(np.array([7.0, 7.0])), [0.5, 0.5]
    )
    expect_value_error(lambda: softmax(np.array([])))
    expect_value_error(lambda: softmax(np.array([np.inf])))
    # Exercise 3: Preserve small contributions
    assert accurate_sum(np.array([1e16, 1.0, -1e16])) == 1.0
    assert accurate_sum(np.array([])) == 0.0
    expect_value_error(lambda: accurate_sum(np.array([np.inf])))
    expect_value_error(lambda: accurate_sum(np.array([1e308, 1e308])))
    # Exercise 4: Promote before multiplying
    a = np.array([2**62], dtype=np.int64)
    b = np.array([4], dtype=np.int64)
    assert floating_dot(a, b) == float(2**64)
    assert floating_dot(np.array([]), np.array([])) == 0
    expect_value_error(lambda: floating_dot(np.array([1]), np.array([1, 2])))
    expect_value_error(lambda: floating_dot(np.array([1e308]), np.array([1e308])))
    # Exercise 5: Separate solver residual from conditioning
    a = np.diag([2.0, 4.0])
    b = np.array([6.0, 8.0])
    x = solve_checked(a, b)
    assert np.allclose(x, [3, 2]) and np.linalg.norm(a @ x - b) < 1e-12
    expect_value_error(lambda: solve_checked(np.ones((2, 2)), np.ones(2)))
    expect_value_error(lambda: solve_checked(np.diag([1.0, 1e-12]), np.ones(2)))
    # Exercise 6: Make numerical comparison semantics explicit
    a = np.array([1e8 + 1, 1e-9])
    b = np.array([1e8, 0.0])
    assert within_tolerance(a, b, 1e-8, 1e-7) and not within_tolerance(a, b, 0, 0)
    assert within_tolerance(np.array([]), np.array([]), 0, 0)
    assert not within_tolerance(np.array([1.7e308]), np.array([-1.7e308]), 0, 1.9)
    assert within_tolerance(np.array([1.7e308]), np.array([-1.7e308]), 0, 2.0)
    expect_value_error(lambda: within_tolerance(np.ones(2), np.ones((1, 2)), 0, 0))
    expect_value_error(lambda: within_tolerance(a, b, -1, 0))
    print("python-numpy-04: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
