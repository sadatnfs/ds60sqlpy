# Day 40 — Solutions: Hyperparameter Tuning with SearchCV

We build a Pipeline, perform parameter search with GridSearchCV/RandomizedSearchCV, and discuss nested CV for unbiased estimates.

Contents
- Exercise 1: GridSearchCV with an SVC pipeline
- Exercise 2: RandomizedSearchCV over a wider parameter space
- Exercise 3: Nested CV (concept + code sketch)

---

Exercise 1 — GridSearchCV + Pipeline (SVC)
```python
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.datasets import load_breast_cancer

X, y = load_breast_cancer(return_X_y=True)

pipe = Pipeline([
    ('sc', StandardScaler()),
    ('svc', SVC(probability=False))
])

param_grid = {
    'svc__C': [0.1, 1, 10],
    'svc__kernel': ['linear', 'rbf'],
    'svc__gamma': ['scale', 'auto']
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
search = GridSearchCV(pipe, param_grid, cv=cv, scoring='roc_auc', n_jobs=-1, refit=True)
search.fit(X, y)
search.best_params_, search.best_score_
```
Line-by-line
- Keep preprocessing (scaler) in the Pipeline to avoid leakage
- Use StratifiedKFold for classification
- scoring='roc_auc' is often better than accuracy for imbalanced data

---

Exercise 2 — RandomizedSearchCV
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform

param_dist = {
    'svc__C': loguniform(1e-3, 1e3),
    'svc__gamma': ['scale', 'auto'],
    'svc__kernel': ['linear', 'rbf']
}

rand = RandomizedSearchCV(pipe, param_distributions=param_dist, n_iter=20,
                          cv=cv, scoring='roc_auc', n_jobs=-1, random_state=0, refit=True)
rand.fit(X, y)
rand.best_params_, rand.best_score_
```
Notes
- RandomizedSearch explores broader spaces efficiently
- Prefer bounded priors (e.g., loguniform for C) for sensible sampling

---

Exercise 3 — Nested CV (sketch)
```python
from sklearn.model_selection import cross_val_score

# inner search for model selection; outer CV for unbiased performance estimate
inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)

inner_search = GridSearchCV(pipe, param_grid, cv=inner, scoring='roc_auc', n_jobs=-1)
outer_scores = cross_val_score(inner_search, X, y, cv=outer, scoring='roc_auc', n_jobs=-1)
{'outer_auc_mean': outer_scores.mean(), 'outer_auc_std': outer_scores.std()}
```
Takeaways
- Tune inside the cross-validation loop to avoid optimistic bias (nested CV)
- Keep all preprocessing inside Pipelines
- Pick metrics aligned with the problem and validate on held-out data
