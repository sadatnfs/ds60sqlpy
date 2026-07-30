# Day 39 — Solutions: Gradient Boosting (sklearn, XGBoost, LightGBM)

We train gradient-boosted tree models, tune key hyperparameters, and use early stopping when supported.

Contents
- Exercise 1: Tune learning_rate and n_estimators (sklearn or XGBoost)
- Exercise 2: Compare XGBoost vs LightGBM (if installed)

---

Setup (scikit-learn and optional XGBoost/LightGBM)
```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_development, X_test, y_development, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_development,
    y_development,
    test_size=0.25,
    random_state=42,
    stratify=y_development,
)
```

Exercise 1 — Sweep learning_rate and n_estimators (sklearn)
```python
learning_rates = [0.03, 0.05, 0.1]
n_estimators_grid = [100, 250, 500]
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
sklearn_results = {}

for learning_rate in learning_rates:
    for n_estimators in n_estimators_grid:
        model = GradientBoostingClassifier(
            learning_rate=learning_rate,
            n_estimators=n_estimators,
            max_depth=3,
            random_state=42,
        )
        mean_auc = cross_val_score(
            model,
            X_development,
            y_development,
            cv=cv,
            scoring="roc_auc",
            n_jobs=1,
        ).mean()
        sklearn_results[(learning_rate, n_estimators)] = mean_auc

top_settings = sorted(
    sklearn_results.items(),
    key=lambda item: item[1],
    reverse=True,
)[:5]
top_settings
```
Notes
- Smaller learning_rate with larger n_estimators is common; tune both
- Consider subsample < 1.0 for stochastic gradient boosting
- The small three-fold sweep is intentionally CPU-safe; expand it only after the pipeline works

Optional: XGBoost with early stopping
```python
try:
    import xgboost as xgb
except ImportError:
    print("Install the 'ml' dependency group to run the XGBoost comparison.")
else:
    xgb_model = xgb.XGBClassifier(
        n_estimators=1_000,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",
        eval_metric="auc",
        early_stopping_rounds=30,
        n_jobs=2,
        random_state=42,
    )
    xgb_model.fit(
        X_train,
        y_train,
        eval_set=[(X_valid, y_valid)],
        verbose=False,
    )
    xgb_auc = roc_auc_score(y_test, xgb_model.predict_proba(X_test)[:, 1])
    {
        "xgb_best_iteration": xgb_model.best_iteration,
        "xgb_test_auc": xgb_auc,
    }
```

Exercise 2 — LightGBM comparison (if installed)
```python
try:
    import lightgbm as lgb
except ImportError:
    print("Install the 'ml' dependency group to run the LightGBM comparison.")
else:
    lgbm_model = lgb.LGBMClassifier(
        n_estimators=1_000,
        learning_rate=0.03,
        num_leaves=31,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.8,
        verbosity=-1,
        random_state=42,
        n_jobs=2,
    )
    lgbm_model.fit(
        X_train,
        y_train,
        eval_set=[(X_valid, y_valid)],
        callbacks=[lgb.early_stopping(30, verbose=False)],
    )
    lgbm_auc = roc_auc_score(y_test, lgbm_model.predict_proba(X_test)[:, 1])
    {
        "lgbm_best_iteration": lgbm_model.best_iteration_,
        "lgbm_test_auc": lgbm_auc,
    }
```
Takeaways
- Use a validation split for early stopping and keep the test split untouched until final scoring
- In current XGBoost, set `early_stopping_rounds` on `XGBClassifier`, not on `fit`
- Tune depth/num_leaves and regularization to control overfitting

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Tune `learning_rate` and `n_estimators` with a simple loop.

**How to reason about it:** Learning rate and estimator count interact: smaller steps usually need more trees. Use identical data boundaries, record runtime, and examine validation curves rather than selecting from training loss.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Compare XGBoost with LightGBM if the `ml` dependency group is installed.

**How to reason about it:** XGBoost and LightGBM have related but non-identical parameters and tree growth strategies. Match the split, metric, seed, and approximate capacity; label the comparison optional when dependencies are unavailable.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Early-stopping design

**Prompt:** Create train, validation, and final test boundaries for early stopping. Explain why using the test set as the early-stopping evaluation set invalidates the final score.

**Reasoning before implementation:** The stopping iteration is a selected hyperparameter. Only the validation set may guide it; the test set remains untouched.

Fit on the training partition, monitor validation loss, retain the best
iteration, and evaluate that frozen procedure once on the test partition.
Record the best iteration because it is part of the fitted artifact.

For limited data, perform early stopping inside outer validation folds or use
a fixed iteration count selected during development. Calling the test set
“eval_set” does not change its statistical role.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 4 — Calibration check

**Prompt:** Compare ROC AUC, log loss, and a reliability diagram for a boosting classifier. Construct an example where ranking is good but probability estimates are overconfident.

**Reasoning before implementation:** AUC depends on ordering; log loss and calibration depend on the numeric probabilities. Use a separate calibration boundary.

A monotonic transformation of scores can preserve ranking and therefore AUC
while making probabilities badly calibrated. Plot predicted-probability bins
against observed event rates and include bin support.

If calibration is needed, wrap the selected estimator with
`CalibratedClassifierCV` using folds or a held-out calibration set. Evaluate
the calibrated result on data used for neither fitting nor calibration.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Portable backend contract

**Prompt:** Design a comparison helper that uses scikit-learn's HistGradientBoostingClassifier offline and adds XGBoost/LightGBM only when installed. It must report skipped backends explicitly.

**Reasoning before implementation:** Detect availability with importlib, keep the baseline unconditional, and never convert a missing optional package into a silent pass.

Return structured records such as `{name, status, metric, seconds, version}`.
The scikit-learn baseline should always run with course dependencies. Optional
imports belong inside their branches, and an unavailable library should
produce `status="skipped"` plus the dependency group needed.

This makes the notebook reproducible on a USB/offline machine without
pretending all implementations ran. Match random seeds and evaluation data,
but document parameters that do not map exactly between libraries.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Overfitting diagnosis

**Prompt:** Plot training and validation loss by boosting iteration and diagnose a curve where training loss falls continuously while validation loss starts rising.

**Reasoning before implementation:** The iteration at minimum validation loss is the candidate stopping point. Also test depth, minimum leaf support, subsampling, and learning rate.

The diverging curves indicate increasing capacity is fitting training-specific
patterns. Early stopping is one response; regularizing tree depth/leaves,
adding row or feature subsampling, or collecting better data may also help.

Do not inspect the final test curve iteration by iteration. That would turn the
test set into another tuning set. Preserve both curves and selected iteration
as training evidence.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
