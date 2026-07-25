# Day 38 — Decision Trees and Random Forests

**Lesson ID:** `python-38` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Decision trees divide feature space through a sequence of rules. Random forests
average many randomized trees to reduce the instability of a single tree.

## Learning objectives

By the end of the lesson, you can:

- fit and compare a decision tree and random forest;
- identify underfitting and overfitting as depth changes;
- control tree complexity with depth and leaf-size settings;
- compare impurity-based and held-out permutation importance; and
- explain why feature importance is not causal importance.

## Prerequisites

- Complete `python-37` (regularized linear models).
- Be able to make a stratified split and interpret accuracy from `python-35`.
- Recall that validation choices must not use the final test set.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Split | Feature threshold that partitions observations at a node |
| Impurity | Measure of class mixing, such as Gini impurity |
| Leaf | Terminal node that produces a prediction |
| Maximum depth | Longest allowed root-to-leaf path |
| Bootstrap sample | Sample drawn with replacement |
| Feature subsampling | Considering only a random subset of features at a split |
| Random forest | Ensemble of decorrelated trees whose predictions are averaged or voted |
| Permutation importance | Score decrease after shuffling one feature in evaluation data |

A deep tree can memorize small idiosyncrasies. A forest reduces variance through
averaging, but it can still learn leakage, bias, and spurious correlations.

## Worked example: compare training and held-out behavior

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42
)

for depth in [1, 2, 4, 8, None]:
    tree = DecisionTreeClassifier(max_depth=depth, random_state=42)
    tree.fit(X_train, y_train)
    print(depth, tree.score(X_train, y_train), tree.score(X_test, y_test))
```

The gap between training and held-out accuracy is one diagnostic, not a complete
model-selection procedure. Choose complexity with validation or CV and report a
separate test estimate.

## Learner exercises

1. Plot tree depth versus accuracy.
2. Inspect feature importances and discuss their reliability.

### Progressive hints

1. Record training and validation accuracy for each depth. Treat `None` as an
   unbounded depth label rather than a numeric x-coordinate.
2. Compare `feature_importances_` with
   `sklearn.inspection.permutation_importance` on held-out data. Preserve feature
   names from `load_breast_cancer().feature_names`.

## Self-check

- Why does a fully grown tree often have very high training accuracy?
- How do bootstrap sampling and feature subsampling decorrelate trees?
- Why can impurity importance favor continuous or high-cardinality features?
- What happens to permutation importance when two features carry redundant
  information?

Expected behavior: very shallow trees underfit, a random forest is generally
more stable than one tree, and the two importance rankings need not match.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Choosing depth on the test set | Optimistic evaluation | Tune in validation/CV |
| Reporting only impurity importance | Biased ranking | Add held-out permutation importance |
| Treating importance as direction | Magnitude has no sign | Use effect-oriented tools and domain analysis |
| Leaving resource use unbounded | Slow or memory-heavy fit | Start with modest `n_estimators` and `n_jobs` |
| Assuming trees need no preprocessing ever | Missing values/categories still require handling | Use a reproducible preprocessing pipeline |

More trees usually reduce Monte Carlo variation but cost CPU and memory.
`min_samples_leaf` is often a more interpretable smoothness control than depth
alone.

## Next step

- Work in the [Day 38 learner notebook](../notebooks/day38_tree_models_random_forest.ipynb).
- Then consult the
  [Day 38 solution](../solutions/day38_tree_models_random_forest/day38_solutions.md).
- Continue to [Day 39 — Gradient Boosting](day39_gradient_boosting_xgboost_lightgbm.md).
