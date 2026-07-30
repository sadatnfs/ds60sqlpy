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

## Learner exercises and progressive hints

1. Sweep `alpha` values and plot validation scores for Ridge and Lasso.
2. Inspect fitted coefficients and compare their sparsity.

The separate solution also demonstrates Elastic Net as a useful extension.

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
4. **Elastic Net implementation:** Build a scaled ElasticNetCV pipeline, state what alpha and l1_ratio control, and inspect both validation behavior and coefficient sparsity.
   **Progressive hint:** Scaling belongs before the estimator; l1_ratio=1 is Lasso-like and 0 is Ridge-like, while alpha controls overall penalty strength.
5. **Scaling bug:** Fit Lasso to one feature measured in dollars and another measured in millions of dollars. Explain why the penalty treats them unfairly without scaling and repair the comparison.
   **Progressive hint:** The L1 penalty operates on coefficient magnitude; rescaling a feature changes the coefficient needed for the same prediction.
6. **Stability investigation:** Create two highly correlated predictors, refit Lasso across several bootstrap samples, and compare selected features with Ridge predictions.
   **Progressive hint:** Lasso may alternate which correlated feature receives weight; Ridge often distributes weight while predictions remain similar.

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
