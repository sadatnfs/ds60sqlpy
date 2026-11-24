# science-023: High-dimensional identification, regularization and validation

Tutorial mode. Stage: advanced. Direct prerequisites: `statistics-learning-006`, `statistics-learning-007`.

## More features can change identification

When the number of predictors exceeds the number of observations, several coefficient vectors can produce the same fitted values. A numerical solver may select one vector by a convention or penalty, but that does not make every coefficient scientifically identified.

For a linear model \(y=X\beta+\epsilon\), the design matrix's rank determines which linear combinations are supported by the observed predictors. Ridge regression adds a quadratic penalty and, for positive \(\lambda\), solves

\[
\widehat\beta_\lambda=(X^{\mathsf T}X+\lambda I)^{-1}X^{\mathsf T}y.
\]

The code uses a linear solve. The penalty can stabilize prediction, but it introduces shrinkage and depends on feature scaling. A unique penalized solution is a consequence of the optimization problem, not proof that each predictor has a separate causal interpretation.

## Key terms

- **Identification:** Whether the data and assumptions determine a unique value of a target quantity.
- **Minimum-norm interpolation:** The least-squares solution with the smallest coefficient norm, which can fit training data exactly when p > n.
- **Ridge regression:** Least squares with a quadratic penalty lambda times the squared coefficient norm, well-posed for every positive lambda.
- **Estimable combination:** A function of coefficients the data determine, such as the sum of two duplicated predictors' coefficients.

## Worked case 1: interpolation does not establish generalization

The synthetic design has 20 observations and 40 predictors, with signal in only the first three coordinates. A minimum-norm least-squares solution interpolates the training outcomes to numerical precision. Its ability to reproduce the observed labels is therefore a weak criterion for selecting a predictive procedure.

A ridge model with a prespecified penalty is evaluated on 50 independent synthetic feature rows. The test error remains positive despite the near-zero interpolation error available in training. The program does not claim that this penalty is optimal. It separates a numerical fitting property from a prediction property under a new sample.

The fixture has a known coefficient vector, making its noiseless test signal available as an oracle. In an external dataset, that signal is not observed. Evaluation typically concerns noisy outcomes, and a test set must match the intended prediction population. Choosing the penalty using those test outcomes would consume the test set as part of model selection.

## Worked case 2: duplicated predictors identify only a sum

The second design has two identical columns. Coefficients \((1,2)\) and \((2,1)\) produce exactly the same fitted values. The matrix has rank one. The code verifies both facts without an optimizer.

An algorithm may nevertheless report one coefficient vector with many decimal places. The reported precision does not resolve the underlying nonidentifiability. A symmetric penalty can select a symmetric solution, while another parameterization or constraint can select something else. Predictions along the observed feature relationship may be stable even when individual coefficients are not.

This distinction matters for feature importance and scientific interpretation. Correlated variables can exchange apparent importance, and selection can be unstable. A variable omitted by one fitted model is not necessarily irrelevant. Its information may be represented through correlated features, or the procedure may lack enough evidence to distinguish alternatives.

## Evaluate the full selection procedure

Preprocessing, feature filtering, scaling, hyperparameter search and model fitting belong inside the training side of an evaluation design. Applying a label-informed filter before cross-validation leaks information into every fold. Even unsupervised transformations should be considered in relation to the actual deployment procedure and data availability.

Nested evaluation can separate selection from assessment, but it does not eliminate uncertainty when the effective sample size is small. Report the resampling unit, selection budget, performance distribution and stability of decisions. Repeatedly inspecting the same evaluation results to invent new features creates additional selection beyond the nominal tuning loop.

High-dimensional inference after variable selection requires additional methods and assumptions. Ordinary regression intervals calculated after a data-driven selection step do not automatically have their usual interpretation. Debiased estimates, selective-inference approaches and sample splitting address different problems; each should be taught through a precise target and conditions rather than as a universal correction.

## Answered scientific discussion

**Can ridge make a singular scientific question identifiable?** It makes a specified penalized optimization problem well-posed. Scientific identification still depends on the information and assumptions supporting the target. The distinction is visible in the duplicated-column example.

**Why not report only test error and ignore coefficients?** That may be appropriate for a bounded prediction task. If a decision requires explanations, transport, causal effects or feature interventions, the instability and meaning of coefficients become relevant again. Define the use before deciding which model properties matter.

## Worked example: Minimum-norm interpolation and a duplicated predictor

```python
import numpy as np

rng = np.random.default_rng(3)
n, p = 6, 20
beta = np.zeros(p)
beta[0] = 2.0
X = rng.normal(size=(n, p))
y = X @ beta + rng.normal(0, 0.5, n)
Xt = rng.normal(size=(200, p))
yt = Xt @ beta + rng.normal(0, 0.5, 200)
b = np.linalg.pinv(X) @ y
print(
    f"train RMSE {np.sqrt(np.mean((X @ b - y) ** 2)):.2e}, test RMSE {np.sqrt(np.mean((Xt @ b - yt) ** 2)):.3f}"
)
print(
    f"test RMSE of the true beta {np.sqrt(np.mean((Xt @ beta - yt) ** 2)):.3f}; of zero {np.sqrt(np.mean(yt**2)):.3f}"
)

x = rng.normal(size=30)
D = np.column_stack([x, x])
yd = 3 * x
for lam in (0.01, 1.0, 10.0):
    coef = np.linalg.solve(D.T @ D + lam * np.eye(2), D.T @ yd)
    print(f"ridge lambda {lam}: coefficients {coef.round(4)}, sum {coef.sum():.4f}")
```

Observed output:

```text
train RMSE 1.62e-15, test RMSE 1.763
test RMSE of the true beta 0.482; of zero 2.130
ridge lambda 0.01: coefficients [1.4998 1.4998], sum 2.9996
ridge lambda 1.0: coefficients [1.48 1.48], sum 2.9600
ridge lambda 10.0: coefficients [1.3216 1.3216], sum 2.6431
```

With six observations and twenty predictors, the minimum-norm least-squares solution fits the training data to \(10^{-15}\), machine precision. On 200 new points its RMSE is 1.763, worse than the true coefficients at 0.482 and barely better than predicting zero at 2.130. A perfect training fit was guaranteed by the dimensions, so it carries no information about generalization; only held-out data revealed the problem. The second part isolates identification. When two columns are identical, any coefficients \((b_1,b_2)\) with \(b_1+b_2=3\) produce the same fitted values, so the data identify only the sum. Ridge resolves the tie by splitting the sum evenly, 1.4998 each at \(\lambda=0.01\). Increasing \(\lambda\) shrinks the sum itself, to 2.96 at 1 and 2.643 at 10. Reporting 1.48, half of the \(\lambda=1\) sum, as the effect of the first predictor would be a statement about the penalty, not the data. The same split appears whenever predictors are nearly collinear.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
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
```

## Primary references

- [Statistical Learning, author-maintained resources](https://www.statlearning.com/)
