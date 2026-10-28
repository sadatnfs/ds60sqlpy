# SVD, Weighted Least Squares, and Low-Rank Approximation

## Level and prerequisites

- **Stable ID:** `python-numpy-07`.
- **Level:** Advanced. Allow about 100 minutes for explanations, prediction and practice; the estimate is not a deadline.
- **Direct prerequisite:** `python-33`, [companion guide](../../ds-60day/companion-guides/day33_linear_algebra_matrices.md).
- **Direct prerequisite:** `python-numpy-02`, [companion guide](py_numpy_02.md).
- **Direct prerequisite:** `python-numpy-04`, [companion guide](py_numpy_04.md).
- **Artifacts:** [learner script](../lessons/py_numpy_07.py) · [explained reference](../solutions/py_numpy_07_solutions.md) · [executable reference](../solutions/py_numpy_07_solution.py).

## How to run this lesson

Run `./classroom` from the repository root, choose **Python** in the shared
`/classroom` directory, and open `python-numpy-07`. Read the capability notice and
use the saved coding pad with the prepared Python Core environment. Docker
supplies Python and NumPy 2.x; no host package install or notebook kernel is
needed. Windows learners use the same entrypoint in WSL 2. Paste the complete
[learner script](../lessons/py_numpy_07.py), save it, and Run its worked
examples before attempting the six task functions. Those functions remain for
you to implement; a passing demonstration does not complete their contracts.

Each browser Run starts a fresh process. Include imports, fixtures and function
calls in the saved source, and save predictions and evidence in your notes.
Temporary arrays and generator objects do not survive the process, whereas the
browser's saved work lives in its Docker learning volume. Use only the tiny
original offline fixtures here; no download, service or database is required.
The [classroom guide](../../../docs/classroom-experience.md) explains that lifecycle.

A separately prepared contributor environment may run
`uv run --no-sync python python/professional/lessons/py_numpy_07.py`
from its checkout. Follow [contributor setup](../../../CONTRIBUTING.md) first;
that environment has separate files and does not import the browser's saved
learning volume. Keep the separate answers closed until you choose to compare
a genuine attempt.

## Learning objectives

This is `python-numpy-07`. Complete `python-33`, `python-numpy-02` and `python-numpy-04` first. You should already recognize matrix multiplication, array axes, ordinary least squares, rank and numerical conditioning. This unit deepens those ideas through weighted objectives, reduced SVD, low-rank error and an augmented ridge system. It does not replace the original Day 33 introduction.

Use the Docker classroom's prepared Python Core environment and the supplied tiny offline matrices. A fresh Run executes the learner's worked examples without needing hidden notebook cells. Your evidence should establish reconstruction identities, objective values and deliberate failures. Do not treat printed singular-vector entries or one successful solver call as the definition of correctness.

By the end of this lesson, you can:

- Verify reduced SVD through reconstruction, factor shapes and orthonormality rather than vector signs.
- Apply an explicit relative rank threshold and measure discarded singular-value error.
- Fit and independently audit a weighted least-squares objective using square-root row scaling.
- Solve ridge regression through an augmented system and explain how its penalty changes the objective.

## Vocabulary and concepts: directions, strengths and reduced shape

**Reduced SVD:** A factorization of a real \(m\)-by-\(n\) matrix \(A\) as

\[
A=U\,\operatorname{diag}(s)\,V^{\mathsf T},\qquad k=\min(m,n).
\]

`U` has shape `(m, k)`, `s` has shape `(k,)`, and NumPy's `Vh` has shape `(k, n)`. The columns of `U` and rows of `Vh` are orthonormal: \(U^{\mathsf T}U=I_k\) and \(V^{\mathsf T}V=I_k\). The singular values are nonnegative and ordered from largest to smallest. They describe how strongly the matrix acts along special input directions.

Reduced does not mean approximate. All \(k\) components still reconstruct the complete matrix up to floating-point error. Approximation begins when components are deliberately discarded. For a tall matrix, `U @ U.T` projects into a column subspace and need not equal the identity on the whole observation space. Confusing these two orthogonality expressions causes false test failures.

**Numerical rank:** A threshold decision about small singular values. Exact algebraic rank and useful numerical rank can differ when measurements or computations contain error.

**Frobenius norm:** The square root of the sum of squared matrix entries; it measures total reconstruction error, rather than the largest error in a single direction.

## Syntax anatomy and invariant checks

`np.linalg.svd(a, full_matrices=False)` requests reduced factors. The expression `(u * s) @ vh` scales columns of `u` by the singular values before multiplication. Broadcasting aligns `s` with the final dimension of `u`; `u * s[:, None]` would express a different operation and may fail only for certain shapes. Use a rectangular fixture to expose that mistake.

Paired singular vectors may flip signs without changing their outer product. If singular values repeat, valid bases within their associated subspace can also rotate. Do not assert a particular sign or copy exact vector entries from one machine. Compare the reconstructed matrix, singular values, orthonormality and appropriate subspace projections with justified tolerances.

## Worked example: discarded strength predicts approximation error

Predict which diagonal entry disappears in the rank-two reconstruction. This complete program uses a diagonal matrix so the approximation can be checked independently of the factorization implementation.

```python
import numpy as np

matrix = np.diag([6.0, 2.0, 0.5])
u, singular, vh = np.linalg.svd(matrix, full_matrices=False)
rank_two = (u[:, :2] * singular[:2]) @ vh[:2]
assert np.allclose(rank_two, np.diag([6, 2, 0]))
assert np.isclose(np.linalg.norm(matrix - rank_two, ord="fro"), 0.5)
assert np.allclose(u.T @ u, np.eye(3))
print("singular values:", singular.tolist(), "tail error:", np.linalg.norm(matrix - rank_two))
```

The omitted component has strength 0.5, so the Frobenius reconstruction error is 0.5 in exact arithmetic. With several discarded components, the error is the square root of their squared strengths, not their simple sum. Changing the retained rank to zero yields a zero matrix and the full matrix norm as the error.

For rank \(r\), the best truncated approximation satisfies

\[
A_r=U_{:,1:r}\operatorname{diag}(s_{1:r})V_{:,1:r}^{\mathsf T},
\qquad
\lVert A-A_r\rVert_F=\sqrt{\sum_{j>r}s_j^2}.
\]

This is a statement about approximation of the supplied matrix. A small reconstruction error does not prove that discarded variation is irrelevant to a later prediction task. A low-energy feature may still encode a rare but important event. Select rank using the purpose and uncertainty of the data, then report the approximation evidence separately.

## Worked example: a weight changes the fitted objective

A row weight determines the cost of its squared residual. Predict which observation contributes nothing to this fit, then run the full example.

```python
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
```

The zero-weight third observation contributes zero cost, so the line through the first two points is the minimizer. It predicts 5 at the third input and does not attempt to match the observed 20. That disagreement is intentional evidence that weights affect the objective; it is not a solver bug.

Replace the zero weight with a positive value and the fit changes. Replacing every weight by ten times itself should preserve the minimizing coefficients within numerical tolerance while multiplying the weighted objective by ten. Multiplying rows by weights instead of square roots would instead square the intended weights, changing relative emphasis.

## Prewhitening and the meaning of weights

Weighted least squares minimizes

\[
J(\beta)=\sum_i w_i(a_i^{\mathsf T}\beta-y_i)^2
=\lVert D A\beta-Dy\rVert_2^2,
\qquad D=\operatorname{diag}(\sqrt{w_i}).
\]

Constructing `D` explicitly is unnecessary: `a * root[:, None]` scales rows, while `y * root` scales the target. This operation is often called prewhitening for independent errors with known relative variances. Inverse-variance weights correspond to a specific statistical model. Arbitrary importance weights define a different objective and should not be described as verified measurement precision.

Nonnegative weights permit ignoring a row; all-zero weights provide no fitting information and are rejected here. Rank-deficient designs remain valid because least squares can choose a minimum-norm coefficient vector. Different coefficient vectors may predict the same observations. Identifiability, residual size and conditioning therefore need separate interpretation.

## Ridge without squaring the conditioning problem

Ridge adds a coefficient penalty:

\[
\lVert A\beta-y\rVert_2^2+\alpha\lVert\beta\rVert_2^2
=\left\lVert
\begin{bmatrix}A\\\sqrt{\alpha}I\end{bmatrix}\beta
-\begin{bmatrix}y\\0\end{bmatrix}
\right\rVert_2^2.
\]

Solve that augmented system with `lstsq`. Forming `A.T @ A` can square the condition number, and explicitly inverting it adds unnecessary numerical work. The augmented route expresses the intended objective directly. Positive regularization shrinks unstable directions, but it also introduces bias and changes the estimation problem.

This unit penalizes every coefficient, including an intercept column if present. Many applications exempt the intercept, which requires a different penalty matrix. Feature units also matter: rescaling one column changes the meaning of an equal penalty on its coefficient. Do not interpret alpha without specifying the design and preprocessing.

## Six exercises

Implement the contracts in `python/professional/lessons/py_numpy_07.py`. For each solver, preserve the original inputs and compute an independently understandable prediction or objective. Tolerances should reflect the fixture's magnitude, while shape checks remain exact.

1. **Verify a reduced factorization: `reduced_svd`.** For a nonempty finite real two-dimensional matrix, return U, s, Vh from np.linalg.svd with full_matrices=False. Reject empty axes, nonmatrices, bool/complex/object/string and nonfinite values with ValueError. Preserve the source. For shape (m, n), k=min(m, n), require shapes (m, k), (k,), (k, n). Validate reconstruction and orthonormality without asserting singular-vector signs.

   **Expected:** For [[3, 0], [0, 2], [0, 0]], s is [3, 2], reconstruction matches input, U.T @ U and Vh @ Vh.T match identity. U @ U.T is not generally the full identity.

2. **State a rank decision policy: `rank_at_tolerance`.** Return the number of singular values strictly greater than rtol times the largest singular value. Require a nonempty finite real matrix and a finite nonnegative scalar rtol, excluding bool. A zero matrix has rank zero. Invalid input raises ValueError. This explicit relative rule intentionally differs from selecting a hidden library default.

   **Expected:** diag([1, 1e-9]) has rank 1 with rtol=1e-8 and rank 2 with rtol=1e-10. Equality at the cutoff is excluded. Multiplying all entries by a moderate positive constant preserves the decision.

3. **Fit a prewhitened system: `weighted_lstsq`.** Fit the minimum-norm least-squares coefficient vector after multiplying each design row and matching target by sqrt(weight). Require nonempty finite real design, matching target vector and finite nonnegative row weights with at least one positive entry. Use np.linalg.lstsq(..., rcond=None). Reject invalid shapes, all-zero weights or nonfinite prewhitened arrays/results with ValueError. Preserve inputs.

   **Expected:** A one-column design of ones, target [0, 4, 100] and weights [1, 3, 0] fits coefficient [3]. A zero weight removes that row from the objective. A rank-deficient design remains valid.

4. **Measure a low-rank approximation: `truncated_svd`.** Return (reconstructed, tail_frobenius_error) for the first rank components of reduced SVD. rank must be an integer from 0 through min(shape), excluding bool. The error value is the Euclidean norm of discarded singular values. Rank zero returns a zero matrix. Reject invalid inputs or nonfinite outputs with ValueError. Preserve the source and return the original matrix shape.

   **Expected:** diag([5, 3, 1]) at rank 1 reconstructs diag([5, 0, 0]) with error \(\sqrt{10}\). Full rank has zero tail error; observed reconstruction error may remain at roundoff scale.

5. **Regularize through an augmented system: `ridge_fit`.** Return coefficients minimizing ||A beta - y|| squared plus alpha times ||beta|| squared. Require a nonempty finite real design, matching target and finite nonnegative alpha excluding bool. Solve the least-squares system formed by stacking A with sqrt(alpha) times the identity, and y with zeros. Penalize every column, including any intercept. Alpha zero follows minimum-norm least squares. Reject invalid inputs or nonfinite results with ValueError.

   **Expected:** With A=identity, y=[2, 4] and alpha=1, return [1, 2]. For duplicate columns and positive alpha, coefficients remain finite. Negative alpha must fail.

6. **Audit the fitted objective independently: `weighted_sse`.** Return sum(weight * (A beta - y)**2) as a finite float for the same real finite design, target and nonnegative-weight policy as weighted_lstsq, with one finite coefficient per column. Reject malformed inputs or an unrepresentable result with ValueError. Do not refit, mutate inputs or rely on the residuals array returned by lstsq.

   **Expected:** The weighted intercept example at beta=[3] has SSE 12; beta=[2] has SSE 16. lstsq may return an empty residuals array for a rank-deficient system, yet this explicit objective remains meaningful.

## Common pitfalls and diagnosis

If reconstruction passes but orthogonality fails, inspect which product you asserted and whether the matrix is rectangular. If rank changes after merely rescaling all data, check whether you used an absolute threshold instead of the declared relative threshold. If coefficients become very large despite tiny residuals, examine singular values and whether the data constrain each direction.

If `lstsq` returns an empty residuals array, recompute the residual explicitly instead of concluding that the residual is zero. That metadata can be empty for rank-deficient or certain shape cases. If changing all weights by a common factor changes the fit materially, inspect prewhitening, numerical scale and the solver's threshold.

Applications include heteroscedastic calibration, compressed matrix storage and regularized linear prediction. None of these tiny examples qualifies a production model. Explain why a vector sign flip is harmless, why a zero weight is different from a missing target, and how ridge changes both stability and the objective. Then construct a rectangular rank-deficient example and defend its evidence without printing an inverse.

## Self-check

Close the examples and answer in your own words before running a confirming case:

- For a tall reduced factorization, explain why `U.T @ U` is identity while `U @ U.T` generally is not.
- Derive the weighted intercept for targets `[0, 4, 100]` and weights `[1, 3, 0]`, then state the objective value at that fit.
- Explain why an empty residuals array from `lstsq` is not proof of zero residual error.
- Describe why a sign-flipped singular-vector pair leaves reconstruction unchanged and why positive ridge penalizes even an intercept under this lesson's contract.

## Next step

Continue to [sliding windows and FFT boundaries](py_numpy_08.md) when you can explain its array and time-series prerequisites. Carry the same distinction between a numerical invariant and a modeling assumption into signal reconstruction.

## Official API references

Use [NumPy's SVD API](https://numpy.org/doc/2.4/reference/generated/numpy.linalg.svd.html) for factor shapes and [the least-squares API](https://numpy.org/doc/2.4/reference/generated/numpy.linalg.lstsq.html) for rank and residual-return conventions.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-07: SVD, Weighted Least Squares, and Low-Rank Approximation.
Read python/professional/companion-guides/py_numpy_07.md and python/professional/lessons/py_numpy_07.py. Direct prerequisites: python-33, python-numpy-02, python-numpy-04. Stay within that boundary and explain new vocabulary at a beginner-friendly pace.
Focus on reduced SVD, rank tolerance, prewhitening, weighted least squares, low-rank error, augmented ridge. Explain one mechanism, ask me to predict a concrete result, let me attempt it, provide one hint at a time, then review my numerical, shape, ownership or exception evidence. Ask retrieval questions that I answer in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use the Docker classroom's prepared Python Core environment with tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database changes, downloads or external services; do not execute any live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a changed-condition failure without copying the reference.
```
