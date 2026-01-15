# Day 39 — Gradient Boosting, XGBoost, LightGBM (Companion Guide)

## Learning objectives
- Understand boosting vs bagging; additive trees trained on residuals
- Tune learning_rate, n_estimators, max_depth/num_leaves
- Use early stopping and evaluate with proper validation

## Why this matters
Gradient-boosted trees dominate many structured-data problems when tuned well.

## Core concepts and examples (sklearn)
```python
from sklearn.ensemble import GradientBoostingClassifier
model = GradientBoostingClassifier(learning_rate=0.05, n_estimators=500, max_depth=3, random_state=0)
model.fit(X_train, y_train)
```

### XGBoost/LightGBM patterns
```python
import xgboost as xgb
xgbm = xgb.XGBClassifier(
    n_estimators=1000, learning_rate=0.05, max_depth=6,
    subsample=0.8, colsample_bytree=0.8, eval_metric='auc', n_jobs=-1, random_state=0
)
xgbm.fit(X_train, y_train, eval_set=[(X_valid,y_valid)], early_stopping_rounds=50, verbose=False)
```

```python
import lightgbm as lgb
lgbm = lgb.LGBMClassifier(
    n_estimators=2000, learning_rate=0.03, num_leaves=63,
    subsample=0.8, colsample_bytree=0.8, metric='auc', random_state=0
)
lgbm.fit(X_train, y_train, eval_set=[(X_valid,y_valid)], callbacks=[lgb.early_stopping(50)])
```

## Common pitfalls
- Too large learning_rate; prefer small lr with more trees + early stopping
- Data leakage in eval_set; build a proper validation split first
- Interpreting default importance without validation

## Practice exercises
1) Tune XGBoost with early stopping; report best iteration
2) Compare LightGBM num_leaves and depth on AUC
3) Plot feature importance and validate with permutation importance

## Further reading
- XGBoost: https://xgboost.readthedocs.io
- LightGBM: https://lightgbm.readthedocs.io
- CatBoost (alternative): https://catboost.ai
