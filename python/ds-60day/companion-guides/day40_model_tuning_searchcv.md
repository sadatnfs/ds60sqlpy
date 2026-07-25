# Day 40 — Hyperparameter Tuning with SearchCV

**Lesson ID:** `python-40` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Hyperparameter search automates a controlled set of model comparisons. It does
not eliminate the need to define a defensible search space, metric, resampling
strategy, or final evaluation boundary.

## Learning objectives

By the end of the lesson, you can:

- address nested pipeline parameters with `step__parameter` names;
- run `GridSearchCV` and `RandomizedSearchCV`;
- use distributions that match parameter scale;
- interpret `best_score_` as an inner validation result; and
- use nested cross-validation for a less biased estimate of a tuning procedure.

## Prerequisites

- Complete `python-39` (gradient boosting).
- Be comfortable with pipelines and stratified CV from `python-34`–`python-35`.
- Understand the distinction between hyperparameters and fitted parameters.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Search space | Declared candidate values or distributions |
| Grid search | Exhaustive Cartesian product of listed candidates |
| Randomized search | Fixed number of samples from parameter distributions |
| Refit | Training the selected configuration on all data supplied to the search |
| Inner CV | Resampling used to select hyperparameters |
| Outer CV | Resampling used to estimate the entire selection procedure |
| Nested CV | Inner search repeated independently inside each outer training fold |

If you evaluate thousands of choices and report the same CV's maximum, selection
noise makes the result optimistic. Nested CV separates selection from estimation.

## Worked example: parameter names follow pipeline structure

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipeline = make_pipeline(StandardScaler(), SVC())
folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(
    pipeline,
    param_grid={
        "svc__C": [0.1, 1.0, 10.0],
        "svc__kernel": ["linear", "rbf"],
    },
    cv=folds,
    scoring="roc_auc",
    n_jobs=2,
    refit=True,
)
search.fit(X, y)
print(search.best_params_, search.best_score_)
```

`best_score_` estimates performance inside the search. It is not a score from an
untouched final test set.

## Learner exercises

1. Use `RandomizedSearchCV` with a wider parameter space.
2. Implement nested cross-validation and compare its result with the non-nested
   search score.

### Progressive hints

1. Sample `C` over orders of magnitude (for example with SciPy's `loguniform`)
   and set `random_state`. Start with about 20 iterations on a laptop.
2. Build separate inner and outer `StratifiedKFold` objects. Pass the entire
   search object—not its already-selected best estimator—to
   `cross_val_score` with the outer splitter.

## Self-check

- Why does a logarithmic distribution make sense for `C`?
- What exactly is retrained when `refit=True`?
- Why should the outer test fold never influence the inner winner?
- When is randomized search more efficient than a full grid?

Expected behavior: nested CV performs many fits and may be slower. Its mean score
can be lower than `best_score_`; that is an expected consequence of a stricter
evaluation boundary, not a failure.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Preprocessing outside the searched pipeline | Fold leakage | Search a complete pipeline |
| Huge grid on a laptop | Combinatorial runtime | Start bounded; use randomized search |
| Default CV ignores groups or time | Invalid independence assumptions | Select a domain-appropriate splitter |
| Repeatedly expanding space after test results | Test-set overfitting | Freeze the search before final evaluation |
| Reporting only winner | Hides instability and cost | Inspect `cv_results_`, spread, and runtime |

Nested CV is computationally expensive: outer folds multiply every inner search
fit. Use it when the risk of tuning optimism warrants that cost, and use a final
held-out set when the project requires a locked evaluation.

## Next step

- Work in the [Day 40 learner notebook](../notebooks/day40_model_tuning_searchcv.ipynb).
- Then consult the
  [Day 40 solution](../solutions/day40_model_tuning_searchcv/day40_solutions.md).
- Continue to [Day 41 — Class Imbalance](day41_imbalance_handling.md).
