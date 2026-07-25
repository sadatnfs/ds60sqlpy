# Day 33 — Linear Algebra and Matrices

**Lesson ID:** `python-33` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

This lesson connects NumPy operations with the geometry underneath linear
models. The goal is practical intuition and reliable computation, not a complete
linear-algebra course.

## Learning objectives

By the end of the lesson, you can:

- predict and verify vector and matrix shapes;
- interpret a dot product, matrix product, norm, rank, and projection;
- add an intercept column to a design matrix;
- solve ordinary least squares without explicitly inverting a matrix; and
- explain how collinearity and conditioning affect numerical stability.

## Prerequisites

- Complete `python-32` (statistical inference).
- Recall NumPy indexing, broadcasting, and array shapes from `python-16`.
- Be comfortable reading a simple linear-regression equation.

## Vocabulary and mental models

| Term | Definition and intuition |
|---|---|
| Vector | Ordered one-dimensional numeric array; a point, direction, or feature row |
| Matrix | Rectangular numeric array; often rows are observations and columns are features |
| Dot product | Sum of elementwise products; measures alignment and produces a scalar |
| Matrix multiplication | Composes linear transformations; inner dimensions must agree |
| Rank | Number of independent directions represented by a matrix |
| Condition number | Sensitivity of a solution to small input changes |
| Projection | Closest point in a subspace under a chosen geometry |
| Pseudoinverse | Generalized inverse that supports least-squares solutions even when a matrix is not invertible |

For a design matrix `X` with shape `(n_samples, n_features)` and coefficients
`w` with shape `(n_features,)`, `X @ w` has one prediction per sample.

## Worked example: solve directly

```python
import numpy as np

rng = np.random.default_rng(0)
X = rng.normal(size=(200, 3))
true_w = np.array([2.0, -1.0, 0.5])
y = X @ true_w + rng.normal(scale=0.5, size=len(X))

# Least-squares solvers use stable decompositions internally.
w_hat, residuals, rank, singular_values = np.linalg.lstsq(X, y, rcond=None)
print(w_hat)
print(rank, singular_values)
```

The notebook shows a pseudoinverse form of the normal equation. It is useful for
understanding the algebra, but production numerical code should prefer
`np.linalg.lstsq` or a tested library estimator. Forming `X.T @ X` squares the
condition number and can amplify error.

## Learner exercises

1. Add an intercept column of ones and recompute the coefficients.
2. Compare the closed-form result with scikit-learn's `LinearRegression` on the
   same data.
3. Explain when the normal equation becomes numerically unstable and why
   iterative methods are often used for larger problems.

### Progressive hints

1. The augmented matrix has one more column. Decide whether the first or last
   coefficient will represent the intercept before inspecting the result.
2. `LinearRegression(fit_intercept=True)` keeps the intercept separate from
   `coef_`; align the two representations before comparing.
3. Construct two almost-duplicate feature columns and inspect
   `np.linalg.cond(X)` or the singular values. Think about both memory and
   computational complexity as dimensions grow.

## Self-check

- Why is `A @ B` generally different from `B @ A`?
- What shape must an intercept column have for 200 observations?
- What does a very small singular value tell you about independent directions?
- Why can coefficients vary dramatically while predictions remain similar when
  features are highly correlated?

Expected behavior: the fitted feature coefficients should be close to
`[2.0, -1.0, 0.5]`, while the estimated intercept should be close to zero
within sampling noise.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Cause | Response |
|---|---|---|
| `matmul` dimension mismatch | Inner dimensions do not agree | Write every operand's shape before multiplying |
| Exact `np.linalg.inv(X.T @ X)` fails | Matrix is singular | Use `lstsq`, `pinv`, regularization, or remove redundancy |
| Coefficients have unexpected scale | Features use different units | Interpret units explicitly; standardize when appropriate |
| Solution changes under tiny perturbations | Poor conditioning | Inspect singular values/condition number and use robust solvers |
| Pseudoinverse is assumed to make inference valid | Numerical solvability confused with statistical assumptions | Check residual structure and data-generating assumptions separately |

Direct solvers are excellent for small dense problems. Iterative solvers reduce
memory and can scale to large or streaming datasets, but require convergence
diagnostics and hyperparameters.

## Next step

- Work in the [Day 33 learner notebook](../notebooks/day33_linear_algebra_matrices.ipynb).
- Compare only after attempting the exercises:
  [Day 33 solution](../solutions/day33_linear_algebra_matrices/day33_solutions.md).
- Continue to [Day 34 — scikit-learn Pipelines](day34_sklearn_intro_pipelines.md).
