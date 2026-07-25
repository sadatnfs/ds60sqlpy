# Day 35 — Model Evaluation and Cross-Validation

**Lesson ID:** `python-35` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Evaluation estimates how a trained procedure will behave on relevant unseen
data. It is not a contest to maximize one score without considering the
decision, the sampling process, and uncertainty.

## Learning objectives

By the end of the lesson, you can:

- select accuracy, precision, recall, F1, ROC AUC, or a regression metric for a
  stated purpose;
- run deterministic stratified cross-validation around a complete pipeline;
- summarize fold scores with both center and variability;
- compare 5-fold and 10-fold estimates without assuming more folds are always
  better; and
- identify leakage caused by preprocessing outside a fold.

## Prerequisites

- Complete `python-34` (scikit-learn pipelines).
- Recall false positives and false negatives.
- Understand that a held-out observation must not influence fitted parameters.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Fold | One partition used as validation while remaining partitions train the model |
| Stratification | Preserving class proportions approximately across folds |
| Cross-validation estimate | Collection of scores from repeated train/validation roles |
| Precision | Fraction of predicted positives that are truly positive |
| Recall | Fraction of actual positives that are found |
| F1 | Harmonic mean of precision and recall at a chosen threshold |
| ROC AUC | Ranking probability across a randomly drawn positive/negative pair |
| Bias–variance tradeoff | Tension between systematic error and sensitivity to sampled data |

Cross-validation evaluates the entire fitting recipe. If feature selection,
scaling, or imputation learns from data, it belongs inside the pipeline that each
fold fits.

## Worked example: make the resampling procedure explicit

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1_000),
)
folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_validate(
    pipeline,
    X,
    y,
    cv=folds,
    scoring={"accuracy": "accuracy", "f1": "f1", "auc": "roc_auc"},
)
```

The metric arrays describe variation across these particular folds; their
standard deviation is not automatically a confidence interval. Report how the
folds were formed so someone else can reproduce the estimate.

## Learner exercises

1. Evaluate the pipeline with `accuracy`, `f1`, and `roc_auc`.
2. Compare the variability from 5-fold and 10-fold cross-validation.
3. Explain leakage risks and how placing preprocessing in a pipeline helps.

### Progressive hints

1. Keep folds identical across metrics. Ask whether each metric uses predicted
   labels, scores, or probabilities.
2. Create two `StratifiedKFold` objects with shuffle and fixed seeds. Compare
   both mean and spread; do not infer a universal rule from one dataset.
3. Sketch what the scaler would know if it were fit before the folds existed.
   Repeat the reasoning for imputation and feature selection.

## Self-check

- Why can accuracy look high when the positive class is rare?
- Does ROC AUC select an operating threshold?
- Why should time-ordered observations usually not use shuffled K-fold CV?
- Which data may be used to choose hyperparameters, and which data should remain
  untouched for a final estimate?

Expected behavior: the package-bundled breast-cancer data runs offline, all
scores lie in their valid ranges, and fold results are similar but not identical.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Response |
|---|---|---|
| Optimizing and reporting on the same holdout repeatedly | Optimistic estimate | Reserve a final holdout or use nested CV |
| Using shuffled folds for temporal/grouped records | Information crosses the boundary | Use time-series or grouped splitters |
| Reporting only the best fold | Selection bias | Report all folds and a declared summary |
| Comparing metric means from different folds | Confounded comparison | Reuse splits for paired comparison |
| Treating fold standard deviation as deployment uncertainty | Different sources of shift ignored | Analyze sampling, subgroup, and temporal stability |

Five folds often balance runtime and training-set size. Ten folds can reduce
training-size bias but costs roughly twice as many fits and does not guarantee
lower variance for every dataset.

## Next step

- Work in the [Day 35 learner notebook](../notebooks/day35_model_evaluation_cv.ipynb).
- Then use the
  [Day 35 solution](../solutions/day35_model_evaluation_cv/day35_solutions.md).
- Continue to [Day 36 — PCA and Feature Selection](day36_dimensionality_reduction_pca.md).
