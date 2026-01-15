# Day 38 — Solutions: Decision Trees and Random Forests

We train a shallow decision tree and a random forest, control overfitting with depth/leaf parameters, and compare feature importances (impurity vs permutation).

Contents
- Exercise 1: Tree depth vs accuracy
- Exercise 2: Feature importances and their reliability

---

Setup
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
```

Exercise 1 — Depth vs accuracy
```python
depths = [1, 2, 3, 4, 6, 8, None]
accs = []
for d in depths:
    dt = DecisionTreeClassifier(max_depth=d, random_state=42)
    dt.fit(Xtr, ytr)
    accs.append(dt.score(Xte, yte))
list(zip(depths, accs))
```
Interpretation
- Very shallow trees underfit; very deep trees may overfit; pick a sweet spot via validation

Random forest baseline
```python
rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=42)
rf.fit(Xtr, ytr)
rf_acc = rf.score(Xte, yte)
rf_acc
```

Exercise 2 — Feature importances (impurity vs permutation)
```python
# Impurity-based (built-in)
impurity_imp = rf.feature_importances_

# Permutation-based (on held-out data)
perm = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=42, n_jobs=-1)
perm_imp = perm.importances_mean

# Compare top features
import numpy as np
order_imp = np.argsort(impurity_imp)[::-1][:10]
order_perm = np.argsort(perm_imp)[::-1][:10]
order_imp, order_perm
```
Notes
- Impurity importances can be biased toward high-cardinality/continuous features
- Prefer permutation importance on a validation set for model-agnostic insight

Takeaways
- Use ensembles (RF) for stronger performance and robustness
- Control overfitting via max_depth/min_samples_leaf and validate choices
