# python-numpy-07: Explained reference solutions

These answers accompany [SVD, Weighted Least Squares, and Low-Rank Approximation](../companion-guides/py_numpy_07.md). Compare after an honest attempt. The [complete standalone executable reference](py_numpy_07_solution.py) includes imports, shared validation helpers and a `main()` that exercises every contract. The snippets below use those helpers; run the complete reference for a fresh-process check. Each named function matches the learner artifact.

## Exercise 1: Verify a reduced factorization

**Contract: `reduced_svd`.** For a nonempty finite real two-dimensional matrix, return U, s, Vh from np.linalg.svd with full_matrices=False. Reject empty axes, nonmatrices, bool/complex/object/string and nonfinite values with ValueError. Preserve the source. For shape (m, n), k=min(m, n), require shapes (m, k), (k,), (k, n). Validate reconstruction and orthonormality without asserting singular-vector signs.

**Expected:** For [[3, 0], [0, 2], [0, 0]], s is [3, 2], reconstruction matches input, U.T @ U and Vh @ Vh.T match identity. U @ U.T is not generally the full identity.

```python
def reduced_svd(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return np.linalg.svd(_matrix(matrix), full_matrices=False)
```

Reduced SVD omits unused null-space columns while retaining all singular values. Multiplying U by the vector s scales its columns by broadcasting, then multiplication by Vh reconstructs the matrix. Signs can flip in paired vectors without changing that product. Repeated singular values allow basis rotation, so compare reconstructed operators and subspaces rather than exact individual vectors.

## Exercise 2: State a rank decision policy

**Contract: `rank_at_tolerance`.** Return the number of singular values strictly greater than rtol times the largest singular value. Require a nonempty finite real matrix and a finite nonnegative scalar rtol, excluding bool. A zero matrix has rank zero. Invalid input raises ValueError. This explicit relative rule intentionally differs from selecting a hidden library default.

**Expected:** diag([1, 1e-9]) has rank 1 with rtol=1e-8 and rank 2 with rtol=1e-10. Equality at the cutoff is excluded. Multiplying all entries by a moderate positive constant preserves the decision.

```python
def rank_at_tolerance(matrix: np.ndarray, rtol: float) -> int:
    a = _matrix(matrix)
    relative = _nonnegative(rtol)
    singular = np.linalg.svd(a, compute_uv=False)
    # Division avoids overflow in rtol * largest_singular_value.
    if singular[0] == 0:
        return 0
    return int(np.count_nonzero(singular / singular[0] > relative))
```

Numerical rank depends on a tolerance and a scale. The ratio comparison is equivalent to the stated rule for a positive largest value and avoids overflowing the product of a large tolerance and singular value. Handle the all-zero matrix before division. A tolerance should reflect precision and application uncertainty; this function exposes the decision rather than claiming one threshold is universally correct.

## Exercise 3: Fit a prewhitened system

**Contract: `weighted_lstsq`.** Fit the minimum-norm least-squares coefficient vector after multiplying each design row and matching target by sqrt(weight). Require nonempty finite real design, matching target vector and finite nonnegative row weights with at least one positive entry. Use np.linalg.lstsq(..., rcond=None). Reject invalid shapes, all-zero weights or nonfinite prewhitened arrays/results with ValueError. Preserve inputs.

**Expected:** A one-column design of ones, target [0, 4, 100] and weights [1, 3, 0] fits coefficient [3]. A zero weight removes that row from the objective. A rank-deficient design remains valid.

```python
def weighted_lstsq(design: np.ndarray, target: np.ndarray, weights: np.ndarray) -> np.ndarray:
    a, b = _system(design, target)
    root = np.sqrt(_weights(weights, a.shape[0]))
    with np.errstate(over="ignore", invalid="ignore"):
        whitened, observed = a * root[:, None], b * root
    if not np.isfinite(whitened).all() or not np.isfinite(observed).all():
        raise ValueError("Prewhitening exceeds finite floating range")
    coefficients = np.linalg.lstsq(whitened, observed, rcond=None)[0]
    if not np.isfinite(coefficients).all():
        raise ValueError("Nonfinite fitted coefficients")
    return coefficients
```

Squaring a sqrt(weight)-scaled residual reproduces weight times residual squared. Scaling by weight itself would optimize a different objective with squared weights. Lstsq handles rank deficiency with a minimum-norm solution at its numerical threshold. There is no inverse of the normal equations here. Multiplying all positive weights by the same moderate factor preserves the minimizer, though objective values rescale.

## Exercise 4: Measure a low-rank approximation

**Contract: `truncated_svd`.** Return (reconstructed, tail_frobenius_error) for the first rank components of reduced SVD. rank must be an integer from 0 through min(shape), excluding bool. The error value is the Euclidean norm of discarded singular values. Rank zero returns a zero matrix. Reject invalid inputs or nonfinite outputs with ValueError. Preserve the source and return the original matrix shape.

**Expected:** diag([5, 3, 1]) at rank 1 reconstructs diag([5, 0, 0]) with error \(\sqrt{10}\). Full rank has zero tail error; observed reconstruction error may remain at roundoff scale.

```python
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
```

For the optimal truncated SVD, the tail norm is the exact Frobenius approximation error in exact arithmetic. This reports the ideal truncation error, not a certified bound on floating-point reconstruction error or data-model error. np.hypot.reduce avoids squaring huge singular values before summation. The theorem concerns matrix approximation, not whether the retained components preserve a downstream classifier or causal interpretation.

## Exercise 5: Regularize through an augmented system

**Contract: `ridge_fit`.** Return coefficients minimizing ||A beta - y|| squared plus alpha times ||beta|| squared. Require a nonempty finite real design, matching target and finite nonnegative alpha excluding bool. Solve the least-squares system formed by stacking A with sqrt(alpha) times the identity, and y with zeros. Penalize every column, including any intercept. Alpha zero follows minimum-norm least squares. Reject invalid inputs or nonfinite results with ValueError.

**Expected:** With A=identity, y=[2, 4] and alpha=1, return [1, 2]. For duplicate columns and positive alpha, coefficients remain finite. Negative alpha must fail.

```python
def ridge_fit(design: np.ndarray, target: np.ndarray, alpha: float) -> np.ndarray:
    a, b = _system(design, target)
    penalty = np.sqrt(_nonnegative(alpha)) * np.eye(a.shape[1])
    augmented = np.vstack((a, penalty))
    observed = np.concatenate((b, np.zeros(a.shape[1])))
    coefficients = np.linalg.lstsq(augmented, observed, rcond=None)[0]
    if not np.isfinite(coefficients).all():
        raise ValueError("Nonfinite fitted coefficients")
    return coefficients
```

The lower block adds alpha times the squared coefficient norm to the residual objective. This solves the intended regularization problem without explicitly constructing A.T @ A or an inverse. The intercept policy is important: applications often exempt it, but this contract penalizes all columns. Feature scaling changes what an equal coefficient penalty means, so preprocessing is part of model design.

## Exercise 6: Audit the fitted objective independently

**Contract: `weighted_sse`.** Return sum(weight * (A beta - y)**2) as a finite float for the same real finite design, target and nonnegative-weight policy as weighted_lstsq, with one finite coefficient per column. Reject malformed inputs or an unrepresentable result with ValueError. Do not refit, mutate inputs or rely on the residuals array returned by lstsq.

**Expected:** The weighted intercept example at beta=[3] has SSE 12; beta=[2] has SSE 16. lstsq may return an empty residuals array for a rank-deficient system, yet this explicit objective remains meaningful.

```python
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
```

Recompute the residual from the original system and the proposed coefficients. This checks a directly observable prediction rather than trusting a solver metadata convention. Its value alone does not prove good conditioning or an appropriate weighting model. Examine perturbations, singular values and domain assumptions as separate evidence. Overflow is rejected rather than returning infinity as if it were a usable score.

## Verification and interpretation

The executable reference covers normal and invalid examples for these contracts. Independent tests in `tests/test_python_numpy_modernization.py` use analytical answers, invariants and changed-condition cases rather than treating the reference output as its own oracle. A reference run is evidence that the implementation meets the tested inputs; explain the relevant assumption and construct an additional counterexample before claiming independent understanding.
