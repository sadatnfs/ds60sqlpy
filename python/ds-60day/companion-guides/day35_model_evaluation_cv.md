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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 35 learner notebook from this guide's **Next
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

## Concept deep dive — metrics, resampling design, and honest generalization estimates

### The mental model

Evaluation begins with the decision, not a convenient default metric.
A confusion matrix records counts at one decision threshold; precision
asks whether positive predictions are reliable, while recall asks how
many actual positives were found. Ranking metrics such as ROC AUC and
average precision evaluate scores across thresholds but do not select
an operating threshold for you.

Cross-validation repeatedly changes which observations train and
validate a model. Its validity depends on the split unit matching the
independence structure. Repeated records from one person, device, or
time period must not leak across folds merely because ordinary K-fold
code runs.

### Worked examples and syntax anatomy

- **`confusion_matrix(y_true, y_pred)`:** returns outcome counts at the selected threshold; inspect label order before unpacking.
- **`cross_validate(estimator, X, y, cv=..., scoring=...)`:** fits a fresh estimator per fold and can report multiple metrics and timing.
- **splitter objects:** encode random, stratified, grouped, or temporal assumptions; `cv=5` is not a universal design.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — derive precision and recall from outcome counts

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score

y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0])
y_pred = np.array([1, 0, 1, 0, 1, 0, 0, 0])
tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
print({"tn": tn, "fp": fp, "fn": fn, "tp": tp,
       "precision": precision, "recall": recall})
assert precision == tp / (tp + fp)
assert recall == tp / (tp + fn)
```

**Expected observation:** Precision is 2/3 and recall is 1/2; the two metrics answer different questions.

**Assumption to name:** Class `1` is the positive class and each error type has a known operational consequence.

### Focused example B — keep entity groups out of each other's folds

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.model_selection import GroupKFold

groups = np.repeat(["A", "B", "C", "D"], 3)
X = np.arange(groups.size).reshape(-1, 1)
y = np.tile([0, 1, 0], 4)
splitter = GroupKFold(n_splits=4)

for train_idx, valid_idx in splitter.split(X, y, groups):
    train_groups = set(groups[train_idx])
    valid_groups = set(groups[valid_idx])
    assert train_groups.isdisjoint(valid_groups)
print("all validation groups were unseen during training")
```

**Expected observation:** Each entity appears entirely in training or validation for a fold, never both.

**Assumption to name:** The group ID captures the dependence that would otherwise create optimistic validation.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define metrics, resampling design, and honest generalization estimates in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Choosing the metric and split after seeing which combination makes the model look best.

**Debug it deliberately:** Write the row grain, positive class, prediction horizon, grouping key, and error costs before constructing the splitter or scorer.

**Stop condition:** Do not compare scores produced from different rows, folds, positive labels, thresholds, or metric definitions.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Evaluate the pipeline with `accuracy`, `f1`, and `roc_auc`.

**Verify:** For task `Evaluate the pipeline with accuracy, f1, and rocauc`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






2. Compare the variability from 5-fold and 10-fold cross-validation.

**Verify:** For task `Compare the variability from 5-fold and 10-fold cross-validation`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.






3. Explain leakage risks and how placing preprocessing in a pipeline helps.

**Verify:** For task `Explain leakage risks and how placing preprocessing in a pipeline helps`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Progressive hints

1. Keep folds identical across metrics. Ask whether each metric uses predicted
   labels, scores, or probabilities.
2. Create two `StratifiedKFold` objects with shuffle and fixed seeds. Compare
   both mean and spread; do not infer a universal rule from one dataset.
3. Sketch what the scaler would know if it were fit before the folds existed.
   Repeat the reasoning for imputation and feature selection.

### Additional mastery practice

Match metrics and resampling to the decision being modeled. Keep thresholds, groups, time, and hyperparameter selection inside honest validation boundaries.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Threshold analysis:** Using one fixed validation score vector, compare confusion matrices at thresholds 0.2, 0.5, and 0.8. Explain which errors increase as the threshold rises and why ROC AUC stays unchanged.
   **Progressive hint:** A higher positive threshold generally reduces predicted positives: false positives fall while false negatives rise. Ranking scores do not change.

**Verify:** For task `Threshold analysis: Using one fixed validation score vector, compare confusion matrices at th...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







5. **Grouped resampling:** Design cross-validation for repeated measurements from the same patient or customer. Demonstrate how ordinary StratifiedKFold can place one entity in both training and validation.
   **Progressive hint:** Use `StratifiedGroupKFold` when both label balance and entity separation matter; assert that train and validation group sets are disjoint.

**Verify:** For task `Grouped resampling: Design cross-validation for repeated measurements from the same patient o...`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







6. **Selection-bias debugging:** Explain why reporting `GridSearchCV.best_score_` as final performance is optimistic. Sketch a nested cross-validation design and distinguish it from out-of-fold predictions for one fixed model.
   **Progressive hint:** The same inner folds both select and report the best candidate. Nested CV puts the complete search inside an outer held-out fold.

**Verify:** For task `Selection-bias debugging: Explain why reporting GridSearchCV.bestscore as final performance i...`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-35` — Day 35 — Model Evaluation and Cross-Validation.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize metrics, resampling design, and honest generalization estimates. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day35_model_evaluation_cv.md`
- learner artifact: `python/ds-60day/notebooks/day35_model_evaluation_cv.ipynb`

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
