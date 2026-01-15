# Day 35 — Solutions: Model Evaluation and Cross-Validation

We evaluate models with appropriate metrics, perform k-fold CV, and discuss bias/variance and leakage.

Contents
- Exercise 1: Compare metrics (accuracy, f1, roc_auc) under CV
- Exercise 2: Compare 5-fold vs 10-fold variability
- Exercise 3: Show how pipelines help prevent leakage

---

Exercise 1 — Metrics with CV
```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

X, y = load_breast_cancer(return_X_y=True)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

clf = Pipeline([
    ('sc', StandardScaler()),
    ('lr', LogisticRegression(max_iter=1000, solver='lbfgs'))
])

scores_acc = cross_val_score(clf, X, y, cv=cv, scoring='accuracy')
scores_f1  = cross_val_score(clf, X, y, cv=cv, scoring='f1')
scores_auc = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc')

{
    'acc_mean': scores_acc.mean(), 'acc_std': scores_acc.std(),
    'f1_mean': scores_f1.mean(),   'f1_std': scores_f1.std(),
    'auc_mean': scores_auc.mean(), 'auc_std': scores_auc.std(),
}
```
Notes
- Use StratifiedKFold for classification to preserve class ratios
- Report mean and variability (std or CI)

---

Exercise 2 — 5-fold vs 10-fold
```python
cv5  = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
cv10 = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
auc5  = cross_val_score(clf, X, y, cv=cv5,  scoring='roc_auc')
auc10 = cross_val_score(clf, X, y, cv=cv10, scoring='roc_auc')
{'auc5_mean': auc5.mean(), 'auc5_std': auc5.std(), 'auc10_mean': auc10.mean(), 'auc10_std': auc10.std()}
```
Observation
- 10-fold gives more train data per fold (less bias), but more variance across folds; compare stds

---

Exercise 3 — Leakage and pipelines
- Scaling and other preprocessing must be fit within each CV fold to avoid peeking at test fold
- Pipelines ensure transform.fit is applied only on training split; transforms then apply to held-out split via transform

Takeaways
- Choose metrics aligned with the business goal (e.g., recall@k for safety-critical)
- Always cross-validate with proper fold type (stratified vs time series)
- Use pipelines to control leakage and keep code reproducible
