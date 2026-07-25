# Day 45 — End-to-End Modeling Mini-Project

**Lesson ID:** `python-45` · **Level:** intermediate · **Dependencies:** `data` · **Network:** first-run Seaborn cache

This checkpoint integrates data loading, leak-safe preprocessing, validation,
evaluation, and a saved pipeline. The objective is reproducible evidence—not the
highest possible score.

## Learning objectives

By the end of the project, you can:

- frame a binary-classification problem and declare an evaluation metric;
- preserve train/test boundaries through a `ColumnTransformer` and `Pipeline`;
- compare a simple baseline with cross-validation and a held-out result;
- save the complete preprocessing-plus-model artifact; and
- document limitations, reproduction steps, and a next experiment.

## Prerequisites

- Complete `python-44` and therefore `python-31` through `python-44`.
- Have a working `data` environment and a writable ignored `artifacts/` folder.
- Cache the Seaborn Titanic dataset while connected before an offline session.

## Dataset and offline contract

The learner notebook calls `seaborn.load_dataset("titanic")`. That first call
may download the small dataset and place it in Seaborn's local cache. This
one-time connected bootstrap is accepted. Once cached, the project can run
offline on that machine.

The separate reference solution uses scikit-learn's package-bundled
breast-cancer dataset to demonstrate the same engineering gates without a
network dependency. It is intentionally a transferable reference, not a
line-for-line Titanic answer.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Baseline | Simple reference that an added-complexity model must justify beating |
| Holdout | Data kept outside fitting and model selection for a final estimate |
| `ColumnTransformer` | Applies different preprocessing to named column groups |
| Reproducibility | Ability to rebuild results from declared code, data, versions, and seeds |
| Artifact | Saved output such as a fitted pipeline, metrics JSON, or plot |
| Acceptance gate | Explicit evidence required before calling a deliverable complete |

## Project gates and evidence

| Gate | Required evidence |
|---|---|
| Problem | Target, prediction unit, intended user, and cost of major error types |
| Data | Columns, missingness, row exclusions, cache requirement, and leakage review |
| Split | Stratified train/holdout split with a fixed seed; holdout untouched during selection |
| Baseline | Named baseline and metric |
| Pipeline | Categories encoded with unknown handling; numeric features processed inside the pipeline |
| Evaluation | Cross-validation scores plus one held-out result and confusion/error analysis |
| Reproducibility | Dependency setup, random states, exact run order, and artifact paths |
| Security/privacy | No secrets or direct identifiers committed; trusted model artifact only |

## Worked pattern: one deployable unit

```python
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

preprocess = ColumnTransformer(
    [
        ("categorical", OneHotEncoder(handle_unknown="ignore"), ["sex", "class"]),
        ("numeric", StandardScaler(), ["fare", "age"]),
    ]
)
pipeline = make_pipeline(
    preprocess,
    LogisticRegression(max_iter=1_000),
)
```

Fit and serialize this complete pipeline, not separately transformed arrays. A
future input must pass through the exact fitted preprocessing.

## Learner exercises and deliverables

The notebook's project checklist is the exercise:

1. Load the dataset and create train/validation/test boundaries.
2. Preprocess with `ColumnTransformer`.
3. Train a baseline model.
4. Evaluate with appropriate metrics and cross-validation.
5. Save the model and preprocessing together with `joblib`.
6. Write a short README-style section in the notebook covering rationale,
   metrics, limitations, and next steps.
7. Optionally adapt the Day 44 FastAPI service.

### Progressive hints

1. Start by writing the target, row unit, and split before feature engineering.
2. Use `handle_unknown="ignore"` for categorical inference and keep every fitted
   transformation inside the pipeline.
3. Report the distribution of fold scores; do not tune against the holdout.
4. Reload the saved artifact in a fresh cell and predict a small valid batch.

## Self-check

- Can a new category pass through the fitted pipeline?
- Can another learner reproduce the split and metric from the notebook alone?
- Did any preprocessing or threshold choice inspect holdout labels?
- Does the saved artifact include both preprocessing and prediction?
- What failure mode would prevent you from recommending deployment?

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Evidence of the problem | Response |
|---|---|---|
| Dropping missing rows without discussion | Cohort changes silently | Quantify removals and possible bias |
| Calling accuracy “the metric” | Error costs remain unstated | Add ROC AUC and thresholded metrics with rationale |
| Comparing many models on the holdout | Score steadily improves through reuse | Return selection to CV; reserve a fresh final set if possible |
| Saving to an arbitrary working directory | Artifact cannot be found/reproduced | Use a documented ignored `artifacts/` path |
| Loading an untrusted model file | Code-execution risk | Load only artifacts produced by this trusted workflow |

This project demonstrates a responsible baseline. It does not establish
production readiness, causal validity, fairness, or stability under future data.

## Next step

- Build in the [Day 45 learner notebook](../notebooks/day45_end_to_end_modeling_project.ipynb).
- Use the differently-dataseted
  [Day 45 reference solution](../solutions/day45_end_to_end_modeling_project/day45_solutions.md)
  only after producing your own evidence.
- Continue to [Day 46 — Deep Learning Overview](day46_deep_learning_overview.md).
