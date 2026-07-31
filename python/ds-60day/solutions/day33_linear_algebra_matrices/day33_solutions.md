# Day 33 — Solutions: Linear Algebra & Matrices for ML Intuition

We implement the normal equation (closed-form least squares), add an intercept, and compare to scikit-learn. We also discuss numerical stability and when to prefer iterative methods.

Contents
- Exercise 1: Add an intercept column and recompute w
- Exercise 2: Compare closed-form solution vs sklearn LinearRegression
- Exercise 3: When normal equation is unstable; why gradient/iterative methods are preferred

---

Setup and synthetic data
```python
import numpy as np
rng = np.random.default_rng(0)

n, d = 200, 3
X = rng.normal(size=(n, d))
true_w = np.array([2.0, -1.0, 0.5])
y = X @ true_w + rng.normal(scale=0.5, size=n)
```

Worked reference for Exercise 1 — Add intercept and recompute w
```python
# Add a column of ones for intercept
X1 = np.c_[np.ones((n, 1)), X]   # shape (n, d+1)

# Normal equation with pseudo-inverse for stability
w_hat = np.linalg.pinv(X1.T @ X1) @ X1.T @ y
w_hat
```
Line-by-line
- np.c_ concatenates a column of 1s to X to model an intercept term
- pinv (Moore–Penrose) is numerically safer than explicit inverse

---

Worked reference for Exercise 2 — Compare to sklearn LinearRegression
```python
from sklearn.linear_model import LinearRegression

lr = LinearRegression(fit_intercept=True)
lr.fit(X, y)

w0 = lr.intercept_
w  = lr.coef_

w0, w
```
Notes
- LinearRegression with fit_intercept=True estimates intercept internally
- Expect close agreement between (w0, w) and the closed-form solution above

---

Worked reference for Exercise 3 — Stability and iterative methods
- Normal equation inverts X^T X (or solves a system); if X has multicollinearity or large condition number, numerical errors grow
- Use np.linalg.lstsq or pinv to mitigate; better yet, rely on QR/SVD inside libraries
- For large n,d or online learning, gradient-based solvers (SGD, coordinate descent) scale better (avoid O(d^3) inversion)

Takeaways
- Prefer library solvers (sklearn) that use robust decompositions
- Add regularization (Ridge/Lasso) when features are collinear or high-dimensional

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`A.shape` and `B.shape`:** state the dimensional contract before multiplication; never infer it from a successful broadcast.
2. **`A @ B`:** performs matrix multiplication, which is different from elementwise `A * B`.
3. **`np.linalg.lstsq(X, y, rcond=None)`:** solves least squares directly and reports rank without explicitly forming an unstable inverse.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Shape reasoning proves the operation is defined, while `lstsq` and rank diagnostics address numerical and identifiability risk.

**Useful alternative:** A pseudoinverse produces a minimum-norm solution, while regularization intentionally trades bias for stability.

**Trade-off:** Centering and scaling improve numerical behavior but change coefficient units and do not create missing information.

**Edge case to test:** An empty matrix, mismatched row counts, NaN/inf values, or a rank-deficient design needs an explicit failure or policy.

**Evidence of correctness:** Assert every intended shape, compare predictions and residuals, report rank/condition, and avoid coefficient interpretation when the design is not identifiable.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Add an intercept column of ones and recompute the coefficients.

**How to reason about it:** Adding a ones column changes X from (rows, features) to (rows, features+1). Decide which coefficient is the intercept and verify predictions by multiplying the augmented matrix by the full coefficient vector.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — matrix shapes, linear transformations, rank, and stable least squares — assert the augmented design has one more column and its first column is all ones; print intercept, slopes, rank, and residual norm, then verify matrix predictions equal the fitted values within 1e-10.

### Exercise 2 — Original lesson practice

**Prompt:** Compare the closed-form result with scikit-learn's `LinearRegression` on the same data.

**How to reason about it:** scikit-learn stores intercept_ separately when fit_intercept=True. Compare both predictions and aligned coefficients on the same inputs; matching rounded coefficients alone can hide a column-order error.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — matrix shapes, linear transformations, rank, and stable least squares — fit both methods to identical X and y with matching intercept policy; print both coefficient vectors and maximum prediction difference, and require predictions to agree within 1e-10.

### Exercise 3 — Original lesson practice

**Prompt:** Explain when the normal equation becomes numerically unstable and why iterative methods are often used for larger problems.

**How to reason about it:** The normal equation magnifies numerical problems when columns are nearly dependent and requires a costly inverse. Use condition number as a warning and `lstsq`/QR/SVD-based solvers as the default.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — matrix shapes, linear transformations, rank, and stable least squares — construct a duplicate or nearly duplicate column, report matrix rank and condition number, and show that a stable least-squares/SVD prediction remains usable while direct normal-equation coefficients become unstable.

### Exercise 4 — Shape tracing

**Prompt:** For X with shape (120, 8), beta with shape (8,), and y with shape (120,), trace the shapes of X.T, X.T @ X, X @ beta, and residuals. Then explain what changes if beta is shaped (8, 1).

**Reasoning before implementation:** Write shapes beside every operand before multiplying. A column vector preserves a trailing dimension that can trigger broadcasting.

`X.T` is `(8, 120)`, `X.T @ X` is `(8, 8)`, `X @ beta` is `(120,)`,
and `(X @ beta) - y` is `(120,)`. With `beta` shaped `(8, 1)`,
the prediction is `(120, 1)`. Subtracting a `(120,)` target from it broadcasts
to `(120, 120)`, a severe bug that can still produce numeric output.

Use `assert prediction.shape == y.shape` at the modeling boundary. Reshape
deliberately with `ravel()` only when a one-dimensional target is truly the
contract.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Shape tracing — print X.T=(8,120), X.T@X=(8,8), X@beta=(120,), and residuals=(120,); with beta=(8,1), assert predictions/residuals are (120,1) only after y is reshaped consistently.

### Exercise 5 — Rank-deficiency debugging

**Prompt:** Construct a design matrix whose third column equals the sum of the first two. Compare `np.linalg.solve(X.T @ X, X.T @ y)` with `np.linalg.lstsq(X, y, rcond=None)` and interpret the rank.

**Reasoning before implementation:** The dependent column makes X.T @ X singular. `lstsq` returns a minimum-norm solution plus rank information without forming an inverse.

An exact linear dependency means multiple coefficient vectors make identical
predictions. A direct solve can raise `LinAlgError` or become unstable, while
least squares reports the deficient rank.

```python
import numpy as np

x1 = np.array([0.0, 1.0, 2.0, 3.0])
x2 = np.array([1.0, 0.0, 1.0, 2.0])
X = np.column_stack([x1, x2, x1 + x2])
y = np.array([1.0, 2.0, 4.0, 6.0])
coefficients, residuals, rank, singular_values = np.linalg.lstsq(
    X, y, rcond=None
)
assert rank == 2
assert np.allclose(X @ coefficients, y, atol=1.0)
```

The coefficient values are not uniquely identifiable. Remove redundant
features, regularize with a documented purpose, or interpret predictions
rather than inventing meaning for unstable individual coefficients.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Rank-deficiency debugging — use a seeded rank-2 matrix with three columns, print rank and condition number, capture solve's singular/unstable result, and assert lstsq predictions have finite values and residual norm matching the projected solution.

### Exercise 6 — Robust vector operation

**Prompt:** Implement cosine similarity for two one-dimensional vectors. Validate equal shapes and define behavior for a zero vector.

**Reasoning before implementation:** Compute dot(a,b)/(norm(a)*norm(b)); a zero norm makes the angle undefined, so do not quietly add an epsilon without documenting it.

```python
import numpy as np

def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    if left.ndim != 1 or right.ndim != 1 or left.shape != right.shape:
        raise ValueError("vectors must be one-dimensional with equal length")
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0.0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    return float(np.dot(left, right) / denominator)

assert np.isclose(
    cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0])),
    0.0,
)
```

Clipping a computed result into `[-1, 1]` can protect a later `arccos` from
tiny floating-point overshoot, but it must not conceal incorrect shapes or a
zero denominator.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Robust vector operation — assert cosine([1,0],[0,1])=0 and cosine(v,v)=1 within 1e-12; reject unequal or non-1D shapes and either raise a documented zero-vector error or return a documented sentinel consistently.
