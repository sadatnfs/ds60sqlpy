# Day 39 — Solutions: Gradient Boosting (sklearn, XGBoost, LightGBM)

We train gradient-boosted tree models, tune key hyperparameters, and use early stopping when supported.

Contents
- Exercise 1: Tune learning_rate and n_estimators (sklearn or XGBoost)
- Exercise 2: Compare XGBoost vs LightGBM (if installed)

---

Setup (sklearn and optional XGBoost/LightGBM)
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```

Exercise 1 — Sweep learning_rate and n_estimators (sklearn)
```python
rates = [0.03, 0.05, 0.1]
ests = [200, 500, 800]
results = {}
for lr in rates:
    for ne in nests:
        gb = GradientBoostingClassifier(learning_rate=lr, n_estimators=ne, max_depth=3, random_state=42)
        auc = cross_val_score(gb, X, y, cv=5, scoring='roc_auc').mean()
        results[(lr, ne)] = auc
# Top settings
sorted(results.items(), key=lambda kv: kv[1], reverse=True)[:5]
```
Notes
- Smaller learning_rate with larger n_estimators is common; tune both
- Consider subsample < 1.0 for stochastic gradient boosting

Optional: XGBoost with early stopping
```python
try:
    from xgboost import XGBClassifier
    xgb = XGBClassifier(
        n_estimators=1000, learning_rate=0.05, max_depth=4,
        subsample=0.8, colsample_bytree=0.8, eval_metric='auc', n_jobs=-1, random_state=42
    )
    xgb.fit(Xtr, ytr, eval_set=[(Xte, yte)], early_stopping_rounds=50, verbose=False)
    auc = roc_auc_score(yte, xgb.predict_proba(Xte)[:,1])
    {'xgb_best_ntrees': xgb.best_ntree_limit, 'xgb_auc': auc}
except Exception as e:
    print('XGBoost not available or failed:', e)
```

Exercise 2 — LightGBM comparison (if installed)
```python
try:
    import lightgbm as lgb
    lgbm = lgb.LGBMClassifier(
        n_estimators=3000, learning_rate=0.03, num_leaves=63,
        subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1
    )
    lgbm.fit(Xtr, ytr, eval_set=[(Xte, yte)], callbacks=[lgb.early_stopping(50, verbose=False)])
    auc = roc_auc_score(yte, lgbm.predict_proba(Xte)[:,1])
    {'lgb_best_iter': lgbm.best_iteration_, 'lgb_auc': auc}
except Exception as e:
    print('LightGBM not available or failed:', e)
```
Takeaways
- Use early stopping with a proper validation split
- Tune depth/num_leaves and regularization to control overfitting
