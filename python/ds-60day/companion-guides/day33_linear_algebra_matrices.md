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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 33 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — matrix shapes, linear transformations, rank, and stable least squares

### The mental model

A vector or matrix is both stored numbers and a transformation with a
shape contract. For `A @ B`, the inner dimensions must agree; the outer
dimensions determine the result. In a design matrix, rows represent
observations and columns represent features. Coefficients map feature
space to predictions.

Least squares chooses coefficients that minimize squared residuals.
Full column rank gives a unique coefficient solution, but near
collinearity can make that solution numerically sensitive. Prediction
may remain stable even while individual coefficients swing, which is
why rank and condition number belong in the diagnostic story.

### Worked examples and syntax anatomy

- **`A.shape` and `B.shape`:** state the dimensional contract before multiplication; never infer it from a successful broadcast.
- **`A @ B`:** performs matrix multiplication, which is different from elementwise `A * B`.
- **`np.linalg.lstsq(X, y, rcond=None)`:** solves least squares directly and reports rank without explicitly forming an unstable inverse.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — trace a matrix product by shape and by hand

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np

observations = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
coefficients = np.array([10.0, -1.0])
predictions = observations @ coefficients
print(observations.shape, coefficients.shape, predictions.shape)
print(predictions)
assert np.array_equal(predictions, np.array([8.0, 26.0, 44.0]))
```

**Expected observation:** A `(3, 2)` matrix multiplied by a `(2,)` vector returns one prediction for each of three rows.

**Assumption to name:** Columns of the matrix and positions in the coefficient vector use the same feature order.

### Focused example B — observe coefficient instability under collinearity

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np

x = np.linspace(0.0, 1.0, 50)
X = np.column_stack([np.ones_like(x), x, x + 1e-10 * np.arange(x.size)])
y = 3.0 + 2.0 * x

coef, residuals, rank, singular_values = np.linalg.lstsq(X, y, rcond=None)
condition = np.linalg.cond(X)
max_prediction_error = np.max(np.abs(X @ coef - y))
print({"rank": rank, "condition": condition,
       "coef": coef, "prediction_error": max_prediction_error})
```

**Expected observation:** The condition number is huge and individual duplicate-feature coefficients are not trustworthy even though predictions are accurate.

**Assumption to name:** The nearly duplicated columns do not represent independently identifiable effects.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define matrix shapes, linear transformations, rank, and stable least squares in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Computing `(X.T @ X) ** -1` or `np.linalg.inv(X.T @ X)` as a default least-squares recipe.

**Debug it deliberately:** Print shapes, rank, singular values, and condition number; compare `lstsq` predictions with the target before interpreting coefficients.

**Stop condition:** Do not assign meaning to a coefficient when feature order, units, rank, or intercept handling is unknown.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Add an intercept column of ones and recompute the coefficients.

**Verify:** For task `Add an intercept column of ones and recompute the coefficients`, show the formula or intermediate quantities and check the final value independently rather than trusting one library call.






2. Compare the closed-form result with scikit-learn's `LinearRegression` on the
   same data.

**Verify:** For task `Compare the closed-form result with scikit-learn's LinearRegression on the`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






3. Explain when the normal equation becomes numerically unstable and why
   iterative methods are often used for larger problems.

**Verify:** For task `Explain when the normal equation becomes numerically unstable and why`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Progressive hints

1. The augmented matrix has one more column. Decide whether the first or last
   coefficient will represent the intercept before inspecting the result.
2. `LinearRegression(fit_intercept=True)` keeps the intercept separate from
   `coef_`; align the two representations before comparing.
3. Construct two almost-duplicate feature columns and inspect
   `np.linalg.cond(X)` or the singular values. Think about both memory and
   computational complexity as dimensions grow.

### Additional mastery practice

Treat shapes, rank, and conditioning as part of every matrix contract. Prefer stable solvers to symbolic formulas that require an explicit inverse.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Shape tracing:** For X with shape (120, 8), beta with shape (8,), and y with shape (120,), trace the shapes of X.T, X.T @ X, X @ beta, and residuals. Then explain what changes if beta is shaped (8, 1).
   **Progressive hint:** Write shapes beside every operand before multiplying. A column vector preserves a trailing dimension that can trigger broadcasting.

**Verify:** For task `Shape tracing: For X with shape (120, 8), beta with shape (8,), and y with shape (120,), trac...`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







5. **Rank-deficiency debugging:** Construct a design matrix whose third column equals the sum of the first two. Compare `np.linalg.solve(X.T @ X, X.T @ y)` with `np.linalg.lstsq(X, y, rcond=None)` and interpret the rank.
   **Progressive hint:** The dependent column makes X.T @ X singular. `lstsq` returns a minimum-norm solution plus rank information without forming an inverse.

**Verify:** For task `Rank-deficiency debugging: Construct a design matrix whose third column equals the sum of the...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







6. **Robust vector operation:** Implement cosine similarity for two one-dimensional vectors. Validate equal shapes and define behavior for a zero vector.
   **Progressive hint:** Compute dot(a,b)/(norm(a)*norm(b)); a zero norm makes the angle undefined, so do not quietly add an epsilon without documenting it.

**Verify:** For task `Robust vector operation: Implement cosine similarity for two one-dimensional vectors. Validat...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-33` — Day 33 — Linear Algebra and Matrices.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize matrix shapes, linear transformations, rank, and stable least squares. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day33_linear_algebra_matrices.md`
- learner artifact: `python/ds-60day/notebooks/day33_linear_algebra_matrices.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
