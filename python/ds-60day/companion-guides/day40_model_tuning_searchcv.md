# Day 40 — Hyperparameter Tuning with SearchCV (Companion Guide)

## Learning objectives
- Use GridSearchCV and RandomizedSearchCV with Pipelines
- Choose CV strategies; use HalvingGrid/Random for efficiency
- Manage scoring, refit, and reproducibility

## Why this matters
Systematic tuning improves performance and robustness while avoiding manual trial-and-error.

## Core concepts and examples
```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold
param_grid = {
  'model__n_estimators': [200, 500, 1000],
  'model__max_depth': [None, 6, 12],
  'model__min_samples_leaf': [1, 2, 4]
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
search = GridSearchCV(pipe, param_grid, cv=cv, scoring='roc_auc', n_jobs=-1, refit=True)
search.fit(X, y)
search.best_params_, search.best_score_
```

### Randomized and Halving
```python
from sklearn.experimental import enable_halving_search_cv  # noqa
from sklearn.model_selection import HalvingRandomSearchCV
```

## Common pitfalls
- Tuning outside a Pipeline and leaking preprocessing
- Using accuracy for imbalanced data; pick appropriate metric
- Too small search space or not enough CV folds

## Practice exercises
1) Build a pipeline and tune tree/forest hyperparameters
2) Compare Grid vs Randomized search efficiency
3) Use HalvingRandomSearchCV and report resource vs score tradeoff

## Further reading
- SearchCV: https://scikit-learn.org/stable/modules/grid_search.html
