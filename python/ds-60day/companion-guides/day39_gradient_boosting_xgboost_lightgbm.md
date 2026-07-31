# Day 39 — Gradient Boosting, XGBoost, and LightGBM

**Lesson ID:** `python-39` · **Level:** intermediate · **Dependencies:** `ml` · **Network:** offline

Gradient boosting builds trees sequentially so each new tree reduces the
current model's loss. XGBoost and LightGBM add efficient implementations and
regularization choices; neither is automatically best for every dataset.

## Learning objectives

By the end of the lesson, you can:

- explain the sequential correction idea behind boosting;
- fit an `XGBClassifier` with deterministic, CPU-friendly settings;
- reason about the interaction of learning rate and number of estimators;
- compare XGBoost and LightGBM under the same split and metric; and
- recognize validation leakage and overfitting during tuning.

## Prerequisites

- Complete `python-38` (trees and random forests).
- Know cross-validation and ROC AUC from `python-35`.
- Install the `ml` dependency group during connected setup; lesson data and
  execution are offline afterward.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Boosting | Sequentially adding weak learners to reduce a loss |
| Learning rate | Shrinkage applied to each new tree's contribution |
| Estimator count | Maximum number of boosting rounds/trees |
| Tree depth / leaves | Controls interaction complexity in each weak learner |
| Subsampling | Training a round on a fraction of rows or features |
| Early stopping | Halting rounds when a separate validation metric no longer improves |
| Regularization | Constraints or penalties that reduce model complexity |

Random forests average independent-ish trees to reduce variance. Boosting
constructs dependent trees to correct errors. The latter can be very accurate
but is sensitive to tuning and validation design.

## Worked example: a bounded offline baseline

```python
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.9,
    colsample_bytree=0.9,
    eval_metric="logloss",
    n_jobs=2,
    random_state=42,
)
model.fit(X_train, y_train)
auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print(f"{auc=:.3f}")
```

This is a survey-scale baseline, not a production prescription. A result on one
small dataset does not establish a universal library winner.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 39 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — sequential boosting, learning-rate budgets, and validation control

### The mental model

Boosting builds an additive model one weak learner at a time. Each new
learner is chosen to reduce the current loss, so later trees focus on
mistakes left by earlier trees. The learning rate shrinks each tree's
contribution; the estimator count controls how many correction steps
are available.

XGBoost and LightGBM implement optimized, regularized variants with
different tree-growth and histogram strategies. Backend names do not
replace experiment design: use the same split, feature contract,
metric, compute budget, and early-stopping boundary when comparing
them.

### Worked examples and syntax anatomy

- **`n_estimators`:** sets the maximum boosting rounds; it interacts strongly with learning rate.
- **`learning_rate`:** shrinks each new tree, often requiring more rounds for similar fit.
- **validation/early stopping:** uses a training-external validation boundary to choose round count; the final test remains untouched.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — watch staged predictions reduce residual error

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

rng = np.random.default_rng(3901)
X = np.linspace(-2, 2, 160).reshape(-1, 1)
y = X[:, 0] ** 2 + rng.normal(scale=0.15, size=X.shape[0])
model = GradientBoostingRegressor(
    n_estimators=40, learning_rate=0.08, max_depth=2, random_state=3901
).fit(X, y)
staged_mse = [
    np.mean((y - prediction) ** 2)
    for prediction in model.staged_predict(X)
]
print({"first": staged_mse[0], "last": staged_mse[-1]})
assert staged_mse[-1] < staged_mse[0]
```

**Expected observation:** Training loss falls as additive correction stages are added; this alone does not prove validation improvement.

**Assumption to name:** The squared-error loss and shallow trees are suitable for this smooth synthetic relationship.

### Focused example B — compare two learning-rate and round-count budgets

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, stratify=y, random_state=3902
)
for rate, rounds in ((0.2, 30), (0.03, 200)):
    model = GradientBoostingClassifier(
        learning_rate=rate, n_estimators=rounds,
        max_depth=2, random_state=3902
    ).fit(X_train, y_train)
    auc = roc_auc_score(y_valid, model.predict_proba(X_valid)[:, 1])
    print({"learning_rate": rate, "rounds": rounds, "valid_auc": auc})
```

**Expected observation:** Different rate/round combinations can achieve similar validation performance, so one hyperparameter cannot be judged alone.

**Assumption to name:** Both candidates receive the same untouched validation rows and metric.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define sequential boosting, learning-rate budgets, and validation control in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Tuning rounds against the final test set or assuming a lower training loss means a better model.

**Debug it deliberately:** Plot training and validation metric by round, record best iteration, compare wall time, and hold all other split/metric choices fixed.

**Stop condition:** Do not compare XGBoost and LightGBM results produced from different preprocessing, row splits, metrics, or early-stopping data.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Tune `learning_rate` and `n_estimators` with a simple loop.

**Verify:** For task `Tune learningrate and nestimators with a simple loop`, demonstrate the concrete requirement “1. Tune learning rate and n estimators with a simple loop” with explicit inputs, observable output, and one counterexample.






2. Compare XGBoost with LightGBM if the `ml` dependency group is installed.

**Verify:** For task `Compare XGBoost with LightGBM if the ml dependency group is installed`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.







### Progressive hints

1. Use a small grid, hold `max_depth` constant, and evaluate all combinations
   with identical folds or an explicit validation set. Record runtime too.
2. Match the split, metric, approximate capacity, and random seed. For LightGBM,
   `num_leaves` plays a related—but not identical—complexity role to depth.

### Additional mastery practice

Control boosting capacity with honest validation, early stopping, and reproducible optional backends. Ranking, calibration, and runtime are separate outcomes.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Early-stopping design:** Create train, validation, and final test boundaries for early stopping. Explain why using the test set as the early-stopping evaluation set invalidates the final score.
   **Progressive hint:** The stopping iteration is a selected hyperparameter. Only the validation set may guide it; the test set remains untouched.

**Verify:** For task `Early-stopping design: Create train, validation, and final test boundaries for early stopping...`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







4. **Calibration check:** Compare ROC AUC, log loss, and a reliability diagram for a boosting classifier. Construct an example where ranking is good but probability estimates are overconfident.
   **Progressive hint:** AUC depends on ordering; log loss and calibration depend on the numeric probabilities. Use a separate calibration boundary.

**Verify:** For task `Calibration check: Compare ROC AUC, log loss, and a reliability diagram for a boosting classi...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







5. **Portable backend contract:** Design a comparison helper that uses scikit-learn's HistGradientBoostingClassifier offline and adds XGBoost/LightGBM only when installed. It must report skipped backends explicitly.
   **Progressive hint:** Detect availability with importlib, keep the baseline unconditional, and never convert a missing optional package into a silent pass.

**Verify:** For task `Portable backend contract: Design a comparison helper that uses scikit-learn's HistGradientBo...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







6. **Overfitting diagnosis:** Plot training and validation loss by boosting iteration and diagnose a curve where training loss falls continuously while validation loss starts rising.
   **Progressive hint:** The iteration at minimum validation loss is the candidate stopping point. Also test depth, minimum leaf support, subsampling, and learning rate.

**Verify:** For task `Overfitting diagnosis: Plot training and validation loss by boosting iteration and diagnose a...`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- Why are a smaller learning rate and larger estimator count often paired?
- Why is a training-set early-stopping target invalid?
- How does row or column subsampling act as regularization?
- Which evidence would justify choosing a slower model with a slightly better
  validation score?

Expected behavior: all data are package-bundled and no model download occurs.
Results can vary by library because algorithms and defaults differ.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely issue | Response |
|---|---|---|
| Training score rises while validation falls | Too much capacity/too many rounds | Reduce complexity or use valid early stopping |
| Comparison favors one library unfairly | Different data, metric, or budget | Hold the experimental protocol constant |
| Laptop becomes unresponsive | Excessive threads/search space | Set `n_jobs` modestly and start with small grids |
| “Best iteration” is unavailable | Early stopping was not configured | Use the installed library's current callback/API deliberately |
| Scores cannot be reproduced | Seeds or split differ | Set split and model random states and log versions |

LightGBM can be extremely fast on larger tabular data; XGBoost has broad tooling
and mature controls. Operational fit, calibration, latency, and maintainability
matter alongside a validation score.

## Next step

- Work in the [Day 39 learner notebook](../notebooks/day39_gradient_boosting_xgboost_lightgbm.ipynb).
- Then review the
  [Day 39 solution](../solutions/day39_gradient_boosting_xgboost_lightgbm/day39_solutions.md).
- Continue to [Day 40 — SearchCV](day40_model_tuning_searchcv.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-39` — Day 39 — Gradient Boosting, XGBoost, and LightGBM.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize sequential boosting, learning-rate budgets, and validation control. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day39_gradient_boosting_xgboost_lightgbm.md`
- learner artifact: `python/ds-60day/notebooks/day39_gradient_boosting_xgboost_lightgbm.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
