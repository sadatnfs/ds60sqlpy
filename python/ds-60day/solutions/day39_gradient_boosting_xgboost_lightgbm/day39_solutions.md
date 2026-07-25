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
