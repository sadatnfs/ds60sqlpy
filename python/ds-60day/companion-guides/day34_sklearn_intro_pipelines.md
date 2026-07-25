# Day 34 — scikit-learn Estimators and Pipelines

**Lesson ID:** `python-34` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

scikit-learn uses a deliberately consistent API. Once you understand estimators,
transformers, and pipelines, you can change models without rewriting the whole
evaluation workflow.

## Learning objectives

By the end of the lesson, you can:

- distinguish `fit`, `transform`, `fit_transform`, `predict`, and `score`;
- make a reproducible train/test split;
- combine preprocessing and a model in a `Pipeline`;
- swap `LinearRegression` for `Ridge` without leaking test information; and
- inspect named steps and interpret standardized coefficients cautiously.

## Prerequisites

- Complete `python-33` (linear algebra and matrices).
- Recall train/validation/test roles from `python-30`.
- Be comfortable with keyword arguments and object methods.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Estimator | Object that learns parameters in `fit` |
| Transformer | Estimator that maps data through `transform` |
| Predictor | Estimator that produces outputs through `predict` |
| Pipeline | Ordered chain whose preprocessing and final estimator share one `fit` call |
| Learned parameter | Value estimated from data, such as `mean_` or `coef_` |
| Hyperparameter | Configuration chosen before fitting, such as Ridge `alpha` |
| Data leakage | Information unavailable at prediction time influencing training or evaluation |
| \(R^2\) | Regression score comparing squared error with a mean-target baseline |

Treat a fitted pipeline as the deployable unit. It preserves the exact
preprocessing learned from training data together with the model.

## Worked example: preprocessing stays inside the boundary

```python
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Pipeline(
    [
        ("scale", StandardScaler()),
        ("ridge", Ridge(alpha=1.0)),
    ]
)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))
```

`StandardScaler.fit` sees only `X_train`. Calling `fit_transform` on the entire
dataset before splitting would leak global means and variances into the test
evaluation.

## Learner exercises

1. Swap `LinearRegression` for `Ridge` and compare test scores.
2. Inspect the coefficients and discuss how feature scaling changes their
   numeric values and interpretation.

### Progressive hints

1. Keep the split and scaler fixed; change only the final named step. Start with
   `alpha=1.0`, then record both models rather than declaring a winner from one
   unexplained number.
2. Reach the fitted model through `pipeline.named_steps`. A coefficient from
   standardized inputs represents a one-standard-deviation feature change, but
   correlated features still complicate causal interpretation.

## Self-check

- Which methods are called on each pipeline step during `fit` and `predict`?
- Why does a fixed `random_state` aid comparison without eliminating sampling
  uncertainty?
- What baseline does a negative test \(R^2\) fail to beat?
- If you save only the final Ridge object, what information is missing?

Expected behavior: both models run from package-bundled data with no network
access. Their test scores may be close; regularization is not guaranteed to win
on one split.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Diagnostic | Better practice |
|---|---|---|
| Scaling before splitting | Scaler was fit on all rows | Put scaling inside the pipeline |
| Comparing different random splits | Models received different examples | Reuse one split or use controlled cross-validation |
| Reading `score` as universal quality | Metric depends on estimator type | Name and interpret the metric explicitly |
| Interpreting coefficients as causal effects | Observational correlations and collinearity remain | Use domain assumptions and uncertainty analysis |
| Mutating a fitted pipeline while experimenting | Results become hard to reproduce | Build fresh pipelines from explicit configurations |

Pipelines add structure and prevent common mistakes, but they do not choose the
right split, metric, or causal assumptions for you.

## Next step

- Work in the [Day 34 learner notebook](../notebooks/day34_sklearn_intro_pipelines.ipynb).
- Then review the
  [Day 34 solution](../solutions/day34_sklearn_intro_pipelines/day34_solutions.md).
- Continue to [Day 35 — Model Evaluation](day35_model_evaluation_cv.md).
