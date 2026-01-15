# Day 38 — Decision Trees and Random Forests (Companion Guide)

## Learning objectives
- Train and interpret decision trees
- Understand bagging and RandomForest hyperparameters
- Evaluate feature importance with caution

## Why this matters
Tree ensembles are strong baselines, robust to scaling, and handle nonlinearities and interactions out of the box.

## Core concepts and examples
```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier

clf = DecisionTreeClassifier(max_depth=4, random_state=0)
clf.fit(X_train, y_train)

rf = RandomForestClassifier(n_estimators=300, max_depth=None,
                            min_samples_leaf=2, n_jobs=-1, random_state=0)
rf.fit(X_train, y_train)

importances = rf.feature_importances_
```

### Tuning ideas
- Increase n_estimators; tune max_depth/min_samples_leaf
- Use oob_score=True for out-of-bag estimate

## Common pitfalls
- Relying on impurity importance with high-cardinality categoricals; prefer permutation importance
- Deep single trees overfit; prefer ensembles

## Practice exercises
1) Visualize a shallow decision tree and interpret splits
2) Compare RF accuracy vs single tree
3) Compute permutation importance and contrast with impurity importance

## Further reading
- Ensembles: https://scikit-learn.org/stable/modules/ensemble.html
