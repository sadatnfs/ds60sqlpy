# Day 39 — Gradient Boosting, XGBoost, and LightGBM

**Lesson ID:** `python-39` · **Level:** intermediate · **Dependencies:** `ml` · **Network:** offline

Gradient boosting builds trees sequentially so each new tree reduces the
current model's loss. XGBoost and LightGBM add efficient implementations and
regularization choices; neither is automatically best for every dataset.

## Learning objectives

By the end of the lesson, you can:

- explain the sequential correction idea behind boosting;
- fit an `XGBClassifier` with deterministic, CPU-friendly settings;
- reason about the interaction of learning rate and number of estimators;
- compare XGBoost and LightGBM under the same split and metric; and
- recognize validation leakage and overfitting during tuning.

## Prerequisites

- Complete `python-38` (trees and random forests).
- Know cross-validation and ROC AUC from `python-35`.
- Install the `ml` dependency group during connected setup; lesson data and
  execution are offline afterward.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Boosting | Sequentially adding weak learners to reduce a loss |
| Learning rate | Shrinkage applied to each new tree's contribution |
| Estimator count | Maximum number of boosting rounds/trees |
| Tree depth / leaves | Controls interaction complexity in each weak learner |
| Subsampling | Training a round on a fraction of rows or features |
| Early stopping | Halting rounds when a separate validation metric no longer improves |
| Regularization | Constraints or penalties that reduce model complexity |

Random forests average independent-ish trees to reduce variance. Boosting
constructs dependent trees to correct errors. The latter can be very accurate
but is sensitive to tuning and validation design.

## Worked example: a bounded offline baseline

```python
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.9,
    colsample_bytree=0.9,
    eval_metric="logloss",
    n_jobs=2,
    random_state=42,
)
model.fit(X_train, y_train)
auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print(f"{auc=:.3f}")
```

This is a survey-scale baseline, not a production prescription. A result on one
small dataset does not establish a universal library winner.

## Learner exercises and progressive hints

1. Tune `learning_rate` and `n_estimators` with a simple loop.
2. Compare XGBoost with LightGBM if the `ml` dependency group is installed.

### Progressive hints

1. Use a small grid, hold `max_depth` constant, and evaluate all combinations
   with identical folds or an explicit validation set. Record runtime too.
2. Match the split, metric, approximate capacity, and random seed. For LightGBM,
   `num_leaves` plays a related—but not identical—complexity role to depth.

### Additional mastery practice

Control boosting capacity with honest validation, early stopping, and reproducible optional backends. Ranking, calibration, and runtime are separate outcomes.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Early-stopping design:** Create train, validation, and final test boundaries for early stopping. Explain why using the test set as the early-stopping evaluation set invalidates the final score.
   **Progressive hint:** The stopping iteration is a selected hyperparameter. Only the validation set may guide it; the test set remains untouched.
4. **Calibration check:** Compare ROC AUC, log loss, and a reliability diagram for a boosting classifier. Construct an example where ranking is good but probability estimates are overconfident.
   **Progressive hint:** AUC depends on ordering; log loss and calibration depend on the numeric probabilities. Use a separate calibration boundary.
5. **Portable backend contract:** Design a comparison helper that uses scikit-learn's HistGradientBoostingClassifier offline and adds XGBoost/LightGBM only when installed. It must report skipped backends explicitly.
   **Progressive hint:** Detect availability with importlib, keep the baseline unconditional, and never convert a missing optional package into a silent pass.
6. **Overfitting diagnosis:** Plot training and validation loss by boosting iteration and diagnose a curve where training loss falls continuously while validation loss starts rising.
   **Progressive hint:** The iteration at minimum validation loss is the candidate stopping point. Also test depth, minimum leaf support, subsampling, and learning rate.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why are a smaller learning rate and larger estimator count often paired?
- Why is a training-set early-stopping target invalid?
- How does row or column subsampling act as regularization?
- Which evidence would justify choosing a slower model with a slightly better
  validation score?

Expected behavior: all data are package-bundled and no model download occurs.
Results can vary by library because algorithms and defaults differ.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely issue | Response |
|---|---|---|
| Training score rises while validation falls | Too much capacity/too many rounds | Reduce complexity or use valid early stopping |
| Comparison favors one library unfairly | Different data, metric, or budget | Hold the experimental protocol constant |
| Laptop becomes unresponsive | Excessive threads/search space | Set `n_jobs` modestly and start with small grids |
| “Best iteration” is unavailable | Early stopping was not configured | Use the installed library's current callback/API deliberately |
| Scores cannot be reproduced | Seeds or split differ | Set split and model random states and log versions |

LightGBM can be extremely fast on larger tabular data; XGBoost has broad tooling
and mature controls. Operational fit, calibration, latency, and maintainability
matter alongside a validation score.

## Next step

- Work in the [Day 39 learner notebook](../notebooks/day39_gradient_boosting_xgboost_lightgbm.ipynb).
- Then review the
  [Day 39 solution](../solutions/day39_gradient_boosting_xgboost_lightgbm/day39_solutions.md).
- Continue to [Day 40 — SearchCV](day40_model_tuning_searchcv.md).
