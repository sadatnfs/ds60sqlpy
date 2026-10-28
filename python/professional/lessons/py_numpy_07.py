"""python-numpy-07: SVD, Weighted Least Squares, and Low-Rank Approximation.

Run the two worked examples, then implement the six independent contracts.
Complete answers are kept in solutions/.
"""

import numpy as np


def reduced_svd(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    For a nonempty finite real two-dimensional matrix, return U, s, Vh from np.linalg.svd
    with full_matrices=False. Reject empty axes, nonmatrices, bool/complex/object/string and
    nonfinite values with ValueError. Preserve the source. For shape (m, n), k=min(m, n),
    require shapes (m, k), (k,), (k, n). Validate reconstruction and orthonormality without
    asserting singular-vector signs.
    """
    raise NotImplementedError("Implement reduced_svd")


def rank_at_tolerance(matrix: np.ndarray, rtol: float) -> int:
    """
    Return the number of singular values strictly greater than rtol times the largest
    singular value. Require a nonempty finite real matrix and a finite nonnegative scalar
    rtol, excluding bool. A zero matrix has rank zero. Invalid input raises ValueError. This
    explicit relative rule intentionally differs from selecting a hidden library default.
    """
    raise NotImplementedError("Implement rank_at_tolerance")


def weighted_lstsq(design: np.ndarray, target: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Fit the minimum-norm least-squares coefficient vector after multiplying each design row
    and matching target by sqrt(weight). Require nonempty finite real design, matching
    target vector and finite nonnegative row weights with at least one positive entry. Use
    np.linalg.lstsq(..., rcond=None). Reject invalid shapes, all-zero weights or nonfinite
    prewhitened arrays/results with ValueError. Preserve inputs.
    """
    raise NotImplementedError("Implement weighted_lstsq")


def truncated_svd(matrix: np.ndarray, rank: int) -> tuple[np.ndarray, float]:
    """
    Return (reconstructed, tail_frobenius_error) for the first rank components of reduced
    SVD. rank must be an integer from 0 through min(shape), excluding bool. The error value
    is the Euclidean norm of discarded singular values. Rank zero returns a zero matrix.
    Reject invalid inputs or nonfinite outputs with ValueError. Preserve the source and
    return the original matrix shape.
    """
    raise NotImplementedError("Implement truncated_svd")


def ridge_fit(design: np.ndarray, target: np.ndarray, alpha: float) -> np.ndarray:
    """
    Return coefficients minimizing ||A beta - y|| squared plus alpha times ||beta|| squared.
    Require a nonempty finite real design, matching target and finite nonnegative alpha
    excluding bool. Solve the least-squares system formed by stacking A with sqrt(alpha)
    times the identity, and y with zeros. Penalize every column, including any intercept.
    Alpha zero follows minimum-norm least squares. Reject invalid inputs or nonfinite
    results with ValueError.
    """
    raise NotImplementedError("Implement ridge_fit")


def weighted_sse(
    design: np.ndarray, target: np.ndarray, weights: np.ndarray, coefficients: np.ndarray
) -> float:
    """
    Return sum(weight * (A beta - y)**2) as a finite float for the same real finite design,
    target and nonnegative-weight policy as weighted_lstsq, with one finite coefficient per
    column. Reject malformed inputs or an unrepresentable result with ValueError. Do not
    refit, mutate inputs or rely on the residuals array returned by lstsq.
    """
    raise NotImplementedError("Implement weighted_sse")


def worked_examples() -> None:
    import numpy as np

    matrix = np.diag([6.0, 2.0, 0.5])
    u, singular, vh = np.linalg.svd(matrix, full_matrices=False)
    rank_two = (u[:, :2] * singular[:2]) @ vh[:2]
    assert np.allclose(rank_two, np.diag([6, 2, 0]))
    assert np.isclose(np.linalg.norm(matrix - rank_two, ord="fro"), 0.5)
    assert np.allclose(u.T @ u, np.eye(3))
    print("singular values:", singular.tolist(), "tail error:", np.linalg.norm(matrix - rank_two))

    import numpy as np

    x = np.array([0.0, 1.0, 2.0])
    design = np.column_stack((np.ones(3), x))
    target = np.array([1.0, 3.0, 20.0])
    weights = np.array([1.0, 1.0, 0.0])
    root = np.sqrt(weights)
    beta = np.linalg.lstsq(design * root[:, None], target * root, rcond=None)[0]
    assert np.allclose(beta, [1, 2])
    assert np.allclose(design[:2] @ beta, target[:2])
    assert not np.isclose(design[2] @ beta, target[2])
    print("coefficients:", beta.tolist(), "ignored-row prediction:", float(design[2] @ beta))


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement and check all six exercise contracts.")

# Exercise 1: Verify a reduced factorization
# Contract: reduced_svd
# Prompt: For a nonempty finite real two-dimensional matrix, return U, s, Vh from np.linalg.svd
# with full_matrices=False. Reject empty axes, nonmatrices, bool/complex/object/string and
# nonfinite values with ValueError. Preserve the source. For shape (m, n), k=min(m, n), require
# shapes (m, k), (k,), (k, n). Validate reconstruction and orthonormality without asserting
# singular-vector signs.
# Expected: For [[3, 0], [0, 2], [0, 0]], s is [3, 2], reconstruction matches input, U.T @ U and
# Vh @ Vh.T match identity. U @ U.T is not generally the full identity.

# Exercise 2: State a rank decision policy
# Contract: rank_at_tolerance
# Prompt: Return the number of singular values strictly greater than rtol times the largest
# singular value. Require a nonempty finite real matrix and a finite nonnegative scalar rtol,
# excluding bool. A zero matrix has rank zero. Invalid input raises ValueError. This explicit
# relative rule intentionally differs from selecting a hidden library default.
# Expected: diag([1, 1e-9]) has rank 1 with rtol=1e-8 and rank 2 with rtol=1e-10. Equality at the
# cutoff is excluded. Multiplying all entries by a moderate positive constant preserves the
# decision.

# Exercise 3: Fit a prewhitened system
# Contract: weighted_lstsq
# Prompt: Fit the minimum-norm least-squares coefficient vector after multiplying each design row
# and matching target by sqrt(weight). Require nonempty finite real design, matching target vector
# and finite nonnegative row weights with at least one positive entry. Use np.linalg.lstsq(...,
# rcond=None). Reject invalid shapes, all-zero weights or nonfinite prewhitened arrays/results
# with ValueError. Preserve inputs.
# Expected: A one-column design of ones, target [0, 4, 100] and weights [1, 3, 0] fits coefficient
# [3]. A zero weight removes that row from the objective. A rank-deficient design remains valid.

# Exercise 4: Measure a low-rank approximation
# Contract: truncated_svd
# Prompt: Return (reconstructed, tail_frobenius_error) for the first rank components of reduced
# SVD. rank must be an integer from 0 through min(shape), excluding bool. The error value is the
# Euclidean norm of discarded singular values. Rank zero returns a zero matrix. Reject invalid
# inputs or nonfinite outputs with ValueError. Preserve the source and return the original matrix
# shape.
# Expected: diag([5, 3, 1]) at rank 1 reconstructs diag([5, 0, 0]) with error sqrt(10). Full rank
# has zero tail error; observed reconstruction error may remain at roundoff scale.

# Exercise 5: Regularize through an augmented system
# Contract: ridge_fit
# Prompt: Return coefficients minimizing ||A beta - y|| squared plus alpha times ||beta|| squared.
# Require a nonempty finite real design, matching target and finite nonnegative alpha excluding
# bool. Solve the least-squares system formed by stacking A with sqrt(alpha) times the identity,
# and y with zeros. Penalize every column, including any intercept. Alpha zero follows minimum-
# norm least squares. Reject invalid inputs or nonfinite results with ValueError.
# Expected: With A=identity, y=[2, 4] and alpha=1, return [1, 2]. For duplicate columns and
# positive alpha, coefficients remain finite. Negative alpha must fail.

# Exercise 6: Audit the fitted objective independently
# Contract: weighted_sse
# Prompt: Return sum(weight * (A beta - y)**2) as a finite float for the same real finite design,
# target and nonnegative-weight policy as weighted_lstsq, with one finite coefficient per column.
# Reject malformed inputs or an unrepresentable result with ValueError. Do not refit, mutate
# inputs or rely on the residuals array returned by lstsq.
# Expected: The weighted intercept example at beta=[3] has SSE 12; beta=[2] has SSE 16. lstsq may
# return an empty residuals array for a rank-deficient system, yet this explicit objective remains
# meaningful.
