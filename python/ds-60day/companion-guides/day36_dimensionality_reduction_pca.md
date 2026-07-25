# Day 36 — Dimensionality Reduction with PCA

**Lesson ID:** `python-36` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Principal component analysis (PCA) rotates numeric data into orthogonal
directions ordered by variance. It can compress correlated features, visualize a
dataset, or denoise measurements, but it does not know the target or preserve
the original feature meanings.

## Learning objectives

By the end of the lesson, you can:

- explain principal components as directions of decreasing variance;
- standardize features before PCA when scale should not determine importance;
- choose a component count from cumulative explained variance;
- compare supervised feature selection with unsupervised feature extraction; and
- place PCA or `SelectKBest` inside cross-validation to avoid leakage.

## Prerequisites

- Complete `python-35` (model evaluation and cross-validation).
- Recall matrix shape, rank, and singular values from `python-33`.
- Be comfortable with scikit-learn pipelines from `python-34`.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Principal component | Unit direction that captures as much remaining variance as possible while staying orthogonal to earlier components |
| Loading | Weight connecting an original feature to a component |
| Score | An observation's coordinate in component space |
| Explained variance ratio | Fraction of dataset variance represented by a component |
| Scree plot | Component index versus individual or cumulative explained variance |
| Feature extraction | Creating new features from combinations of originals |
| Feature selection | Retaining a subset of original features |

PCA preserves variance, not class separation, fairness, causal structure, or
semantic importance. A low-variance feature can still be highly predictive.

## Worked example: scale, fit, inspect

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
projection = make_pipeline(StandardScaler(), PCA())
X_components = projection.fit_transform(X)

pca = projection.named_steps["pca"]
cumulative = np.cumsum(pca.explained_variance_ratio_)
components_for_95 = int(np.searchsorted(cumulative, 0.95) + 1)
print(cumulative, components_for_95)
```

The scaler and PCA must be fitted inside each training fold when measuring model
performance. Fitting them once on the full dataset gives validation folds
information about global means, variances, and component directions.

## Learner exercises

1. Plot cumulative explained variance and choose a component count.
2. Compare PCA before and after feature standardization.
3. Try `SelectKBest` on a classification dataset and compare its validated
   performance with PCA.

### Progressive hints

1. Fit all possible components first, then use `np.cumsum`. Declare a threshold
   such as 95% before looking for the first component count that crosses it.
2. Compare both the variance ratios and two-dimensional scatter plots. Iris
   features use different physical units and spreads.
3. Put each alternative in its own pipeline. `f_classif` sees the target; PCA
   does not, so the comparison includes an interpretability tradeoff.

## Self-check

- Why can a component's sign flip without changing the PCA solution?
- When does scaling before PCA change the question being asked?
- Why must target-aware selection happen inside each training fold?
- Can you reconstruct the original data exactly after retaining only two
  components? What determines the reconstruction error?

Expected behavior: cumulative explained variance is nondecreasing and ends near
1 when all components are retained.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Diagnostic | Response |
|---|---|---|
| One high-variance unit dominates | Raw and scaled results differ greatly | Decide whether raw scale has domain meaning |
| PCA fitted before cross-validation | Validation data influenced directions | Put PCA in a pipeline |
| Loadings treated as causal effects | Components are associations | Use cautious, domain-informed interpretation |
| Component count selected from test performance | Test set becomes tuning data | Select in training/CV, evaluate once on holdout |
| PCA applied indiscriminately to categories | Numeric geometry is artificial | Encode with a method suited to the feature and goal |

Compression can reduce runtime and collinearity. It also obscures feature
meaning and may remove predictive low-variance signals. Validate the complete
downstream objective.

## Next step

- Work in the [Day 36 learner notebook](../notebooks/day36_dimensionality_reduction_pca.ipynb).
- Then review the
  [Day 36 solution](../solutions/day36_dimensionality_reduction_pca/day36_solutions.md).
- Continue to [Day 37 — Regularization](day37_regularization_linear_models.md).
