"""Complete offline references for python-numpy-07; no normal-equation inversion."""

from collections.abc import Callable

import numpy as np


def _real(values: np.ndarray) -> np.ndarray:
    source = np.asarray(values)
    if source.dtype.kind not in "iuf":
        raise ValueError("Expected real numeric values, excluding bool")
    result = source.astype(np.float64)
    if not np.isfinite(result).all():
        raise ValueError("Expected finite values")
    return result


def _matrix(values: np.ndarray) -> np.ndarray:
    matrix = _real(values)
    if matrix.ndim != 2 or min(matrix.shape) == 0:
        raise ValueError("Expected a nonempty matrix")
    return matrix


def _system(design: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a, b = _matrix(design), _real(target)
    if b.shape != (a.shape[0],):
        raise ValueError("Target must be a vector with one value per row")
    return a, b


def _weights(weights: np.ndarray, rows: int) -> np.ndarray:
    w = _real(weights)
    if w.shape != (rows,) or np.any(w < 0) or not np.any(w > 0):
        raise ValueError("Expected nonnegative row weights with at least one positive value")
    return w


def _nonnegative(value: float) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, float, np.integer, np.floating)
    ):
        raise ValueError("Expected a finite nonnegative scalar")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError("Expected a finite nonnegative scalar") from error
    if not np.isfinite(result) or result < 0:
        raise ValueError("Expected a finite nonnegative scalar")
    return result


def reduced_svd(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return np.linalg.svd(_matrix(matrix), full_matrices=False)


def rank_at_tolerance(matrix: np.ndarray, rtol: float) -> int:
    a = _matrix(matrix)
    relative = _nonnegative(rtol)
    singular = np.linalg.svd(a, compute_uv=False)
    # Division avoids overflow in rtol * largest_singular_value.
    if singular[0] == 0:
        return 0
    return int(np.count_nonzero(singular / singular[0] > relative))


def weighted_lstsq(design: np.ndarray, target: np.ndarray, weights: np.ndarray) -> np.ndarray:
    a, b = _system(design, target)
    root = np.sqrt(_weights(weights, a.shape[0]))
    with np.errstate(over="ignore", invalid="ignore"):
        whitened, observed = a * root[:, None], b * root
    if not np.isfinite(whitened).all() or not np.isfinite(observed).all():
        raise ValueError("Prewhitening exceeds finite floating range")
    coefficients: np.ndarray = np.linalg.lstsq(whitened, observed, rcond=None)[0]
    if not np.isfinite(coefficients).all():
        raise ValueError("Nonfinite fitted coefficients")
    return coefficients


def truncated_svd(matrix: np.ndarray, rank: int) -> tuple[np.ndarray, float]:
    a = _matrix(matrix)
    if (
        isinstance(rank, (bool, np.bool_))
        or not isinstance(rank, (int, np.integer))
        or not 0 <= rank <= min(a.shape)
    ):
        raise ValueError("Rank must be an integer from zero through min(shape)")
    u, singular, vh = reduced_svd(a)
    with np.errstate(over="ignore", invalid="ignore"):
        reconstructed = (u[:, :rank] * singular[:rank]) @ vh[:rank, :]
    # hypot.reduce evaluates a Euclidean length without squaring huge values first.
    error = float(np.hypot.reduce(singular[rank:], initial=0.0))
    if not np.isfinite(reconstructed).all() or not np.isfinite(error):
        raise ValueError("Approximation or error exceeds finite floating range")
    return reconstructed, error


def ridge_fit(design: np.ndarray, target: np.ndarray, alpha: float) -> np.ndarray:
    a, b = _system(design, target)
    penalty = np.sqrt(_nonnegative(alpha)) * np.eye(a.shape[1])
    augmented = np.vstack((a, penalty))
    observed = np.concatenate((b, np.zeros(a.shape[1])))
    coefficients: np.ndarray = np.linalg.lstsq(augmented, observed, rcond=None)[0]
    if not np.isfinite(coefficients).all():
        raise ValueError("Nonfinite fitted coefficients")
    return coefficients


def weighted_sse(
    design: np.ndarray, target: np.ndarray, weights: np.ndarray, coefficients: np.ndarray
) -> float:
    a, b = _system(design, target)
    w = _weights(weights, a.shape[0])
    beta = _real(coefficients)
    if beta.shape != (a.shape[1],):
        raise ValueError("Expected one coefficient per design column")
    with np.errstate(over="ignore", invalid="ignore"):
        positive = w > 0
        residual = np.sqrt(w[positive]) * (a[positive] @ beta - b[positive])
        result = float(residual @ residual)
    if not np.isfinite(result):
        raise ValueError("Weighted residual sum exceeds finite floating range")
    return result


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    a = np.array([[3.0, 0.0], [0.0, 2.0], [0.0, 0.0]])
    u, singular, vh = reduced_svd(a)
    assert u.shape == (3, 2) and singular.shape == (2,) and vh.shape == (2, 2)
    np.testing.assert_allclose((u * singular) @ vh, a, atol=1e-12)
    np.testing.assert_allclose(u.T @ u, np.eye(2), atol=1e-12)
    np.testing.assert_allclose(vh @ vh.T, np.eye(2), atol=1e-12)
    assert rank_at_tolerance(np.diag([1.0, 1e-9]), 1e-8) == 1
    assert rank_at_tolerance(np.zeros((2, 3)), 0) == 0
    expect_value_error(lambda: rank_at_tolerance(a, -1))
    design, target, weights = (
        np.ones((3, 1)),
        np.array([0.0, 4.0, 100.0]),
        np.array([1.0, 3.0, 0.0]),
    )
    beta = weighted_lstsq(design, target, weights)
    np.testing.assert_allclose(beta, [3.0], atol=1e-12)
    expect_value_error(lambda: weighted_lstsq(design, target, np.zeros(3)))
    low, error = truncated_svd(a, 1)
    np.testing.assert_allclose(low, [[3, 0], [0, 0], [0, 0]], atol=1e-12)
    assert np.isclose(error, 2) and np.isclose(np.linalg.norm(a - low), error)
    assert truncated_svd(a, 0)[0].shape == a.shape
    expect_value_error(lambda: truncated_svd(a, True))
    np.testing.assert_allclose(ridge_fit(np.eye(2), np.array([2.0, 4.0]), 1), [1, 2], atol=1e-12)
    expect_value_error(lambda: ridge_fit(a, np.ones(3), -1))
    assert np.isclose(weighted_sse(design, target, weights, beta), 12)
    assert weighted_sse(design, target, weights, np.array([2.0])) > 12
    expect_value_error(lambda: weighted_sse(design, target, weights, np.array([1.0, 2.0])))
    print("python-numpy-07: six SVD, weighted fit, and ridge contracts passed")


if __name__ == "__main__":
    main()
