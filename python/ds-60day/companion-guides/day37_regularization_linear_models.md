# Day 37 — Regularization and Linear Models

**Lesson ID:** `python-37` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Regularization changes the fitting objective by penalizing coefficient size.
The goal is controlled generalization, not simply making every coefficient
small.

## Learning objectives

By the end of the lesson, you can:

- contrast Ridge (L2), Lasso (L1), and Elastic Net penalties;
- explain why numeric scaling matters before penalization;
- sweep regularization strength with cross-validation;
- compare coefficient shrinkage and sparsity; and
- diagnose underfitting, convergence warnings, and unstable feature selection.

## Prerequisites

- Complete `python-36` (PCA and feature selection).
- Recall linear-model coefficients from `python-33`.
- Be able to evaluate a pipeline with cross-validation from `python-35`.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Regularization | Adding a complexity penalty to the data-fitting loss |
| Ridge / L2 | Penalty proportional to the sum of squared coefficients |
| Lasso / L1 | Penalty proportional to the sum of absolute coefficients |
| Elastic Net | Weighted mixture of L1 and L2 penalties |
| `alpha` | Penalty strength in these scikit-learn estimators |
| Sparsity | Many coefficients exactly zero |
| Shrinkage | Moving estimated coefficients toward zero |

With standardized features, the penalty treats one coefficient unit
consistently across columns. Without scaling, a feature's measurement unit can
determine how strongly it is penalized.

## Worked example: inspect validation and coefficients

```python
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_diabetes(return_X_y=True)
alphas = np.logspace(-3, 1, 8)

for alpha in alphas:
    model = make_pipeline(
        StandardScaler(),
        Lasso(alpha=alpha, max_iter=20_000),
    )
    mean_r2 = cross_val_score(model, X, y, cv=5, scoring="r2").mean()
    print(f"{alpha=:.4f} {mean_r2=:.3f}")
```

A stronger penalty usually increases bias and decreases variance, but the
validation curve is empirical. Select `alpha` using training folds rather than
the final test set.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 37 learner notebook from this guide's **Next
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

## Concept deep dive — regularization strength, coefficient shrinkage, sparsity, and stability

### The mental model

Linear models minimize a data-fitting loss. Regularization adds a cost
for coefficient size: Ridge uses squared coefficients (L2), Lasso uses
absolute coefficients (L1), and Elastic Net combines them. Increasing
`alpha` gives the penalty more influence, usually increasing bias while
reducing variance.

The penalty acts on coefficient magnitudes, so feature units matter.
Standardization makes one unit of coefficient more comparable across
numeric features. Lasso's zero coefficients are a property of the
fitted sample and penalty, not proof that excluded features are
irrelevant or causally unimportant.

### Worked examples and syntax anatomy

- **`Pipeline([('scale', StandardScaler()), ('model', Ridge(...))])`:** learns scaling inside each training boundary before applying the penalty.
- **`alpha`:** controls penalty strength; compare it on a logarithmic scale with cross-validation.
- **`model.coef_`:** contains coefficients in transformed feature space; inspect magnitude and stability alongside validation error.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — trace Ridge shrinkage as alpha grows

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

X, y = make_regression(n_samples=250, n_features=8, noise=20, random_state=3701)
Xs = StandardScaler().fit_transform(X)
norms = {}
for alpha in (0.01, 1.0, 100.0):
    coef = Ridge(alpha=alpha).fit(Xs, y).coef_
    norms[alpha] = np.linalg.norm(coef)
print(norms)
assert norms[0.01] > norms[1.0] > norms[100.0]
```

**Expected observation:** The L2 norm of the coefficient vector decreases as penalty strength increases.

**Assumption to name:** The same scaled design and response are used for every alpha so only regularization changes.

### Focused example B — distinguish Lasso sparsity from stable selection

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

X, y = make_regression(n_samples=120, n_features=20, n_informative=5,
                       noise=25, random_state=3702)
Xs = StandardScaler().fit_transform(X)
for alpha in (0.1, 1.0, 10.0):
    coef = Lasso(alpha=alpha, max_iter=20_000).fit(Xs, y).coef_
    print(alpha, {"nonzero": np.count_nonzero(coef),
                  "largest_abs": np.max(np.abs(coef))})
```

**Expected observation:** Stronger L1 regularization generally produces more exact zeros, but selected columns can change with data and alpha.

**Assumption to name:** The optimization converged; warnings and `n_iter_` were inspected rather than ignored.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define regularization strength, coefficient shrinkage, sparsity, and stability in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Comparing penalized coefficients from unscaled features and interpreting the largest numeric coefficient as most important.

**Debug it deliberately:** Inspect feature scales, convergence warnings, coefficient paths, fold scores, and selection frequency across resamples.

**Stop condition:** Do not claim feature selection stability from one split or choose alpha from final test performance.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Sweep `alpha` values and plot validation scores for Ridge and Lasso.

**Verify:** Practice 1 — regularization strength, coefficient shrinkage, sparsity, and stability — evaluate Ridge and Lasso over one declared logarithmic alpha grid with identical folds; save a labeled validation-score curve, print the selected alpha/mean/std for each model, and leave the final test set untouched.

2. Inspect fitted coefficients and compare their sparsity.

The separate solution also demonstrates Elastic Net as a useful extension.

**Verify:** Practice 2 — regularization strength, coefficient shrinkage, sparsity, and stability — print a feature-aligned coefficient table for Ridge and Lasso, define the near-zero tolerance used for sparsity, and report each nonzero count plus validation metric from the same scaled pipeline.

### Progressive hints

1. Use a logarithmic grid and a log-scaled x-axis because meaningful penalty
   strengths often span orders of magnitude. Keep folds identical.
2. Fit the chosen pipelines on the same training data. Access the final model
   through `named_steps` and count values equal or very close to zero.

### Additional mastery practice

Connect regularization strength to coefficient geometry, validation, and feature scaling. Sparse or stable coefficients are model behaviors, not causal truths.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Prediction:** Predict the coefficient and training-error behavior of Ridge as alpha moves from nearly zero to an extremely large value. Identify what happens to an unpenalized intercept.
   **Progressive hint:** Larger alpha increases shrinkage and bias; most standard estimators exclude the intercept from the penalty.

**Verify:** Prediction — print Ridge coefficients, intercept, and training error for alpha near 0, 1, and 1e6; verify slopes shrink toward zero, the unpenalized intercept remains free, and training error does not improve as the penalty dominates.

4. **Elastic Net implementation:** Build a scaled ElasticNetCV pipeline, state what alpha and l1_ratio control, and inspect both validation behavior and coefficient sparsity.
   **Progressive hint:** Scaling belongs before the estimator; l1_ratio=1 is Lasso-like and 0 is Ridge-like, while alpha controls overall penalty strength.

**Verify:** Elastic Net implementation — print ElasticNetCV selected alpha/l1_ratio, every validation score summary, coefficient table, and nonzero count under a declared tolerance; assert scaling is inside the fitted pipeline.

5. **Scaling bug:** Fit Lasso to one feature measured in dollars and another measured in millions of dollars. Explain why the penalty treats them unfairly without scaling and repair the comparison.
   **Progressive hint:** The L1 penalty operates on coefficient magnitude; rescaling a feature changes the coefficient needed for the same prediction.

**Verify:** Scaling bug — fit the same Lasso problem before/after scaling, print feature scales and original-unit coefficients, and show the scaled pipeline removes unit-dependent penalty unfairness while producing finite validation metrics.

6. **Stability investigation:** Create two highly correlated predictors, refit Lasso across several bootstrap samples, and compare selected features with Ridge predictions.
   **Progressive hint:** Lasso may alternate which correlated feature receives weight; Ridge often distributes weight while predictions remain similar.

**Verify:** Stability investigation — over declared bootstrap seeds, print Lasso selected-feature indicators/frequencies and Ridge prediction variability; report the predictor correlation and show whether Lasso selection swaps while Ridge predictions remain comparatively stable.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why does Ridge rarely produce exact zeros while Lasso can?
- What does a very large `alpha` do to training fit and model flexibility?
- Why can Lasso select one arbitrary member of a correlated feature group?
- Which two hyperparameters does Elastic Net expose conceptually?

Expected behavior: overly large penalties underfit; Lasso generally produces
more zeros than Ridge at useful strengths, though exact outcomes depend on data
and `alpha`.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| `ConvergenceWarning` from Lasso | Too few iterations, poor scaling, or hard optimization | Scale, raise `max_iter`, and inspect convergence |
| All coefficients become zero | Penalty too strong | Expand the search toward smaller `alpha` |
| Coefficient comparison is misleading | Different feature units | Keep `StandardScaler` inside the pipeline |
| Sparse features change across resamples | Correlated predictors or limited data | Check selection stability; consider Elastic Net |
| Best score selected from final holdout | Evaluation leakage | Tune with CV, reserve the holdout |

Sparsity may improve deployment and interpretation, but zero coefficients are
not proof that a feature is irrelevant or causally unimportant.

## Next step

- Work in the [Day 37 learner notebook](../notebooks/day37_regularization_linear_models.ipynb).
- Then compare with the
  [Day 37 solution](../solutions/day37_regularization_linear_models/day37_solutions.md).
- Continue to [Day 38 — Trees and Random Forests](day38_tree_models_random_forest.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-37` — Day 37 — Regularization and Linear Models.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize regularization strength, coefficient shrinkage, sparsity, and stability. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day37_regularization_linear_models.md`
- learner artifact: `python/ds-60day/notebooks/day37_regularization_linear_models.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-36`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
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
