# Day 41 — Handling Class Imbalance

**Lesson ID:** `python-41` · **Level:** intermediate · **Dependencies:** `ml` · **Network:** offline

An imbalanced target is not automatically a problem. It becomes a modeling
problem when the minority outcome matters and the chosen metric or decision
threshold hides poor performance on it.

## Learning objectives

By the end of the lesson, you can:

- quantify target prevalence before fitting a model;
- interpret precision, recall, F1, average precision, and ROC AUC under imbalance;
- compare class weighting with training-only resampling;
- tune a probability threshold without using final test labels; and
- explain why synthetic resampling does not create new real-world evidence.

## Prerequisites

- Complete `python-40` (hyperparameter search).
- Recall classification metrics from `python-35`.
- Install the `ml` dependency group during bootstrap for `imbalanced-learn`.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Prevalence | Fraction of observations in the positive class |
| Class weight | Multiplier that changes how much each class contributes to training loss |
| Resampling | Changing training class frequencies through over- or undersampling |
| SMOTE | Synthesizing minority examples between nearby minority observations |
| Decision threshold | Score boundary converted into a class label |
| Precision–recall curve | Precision and recall across thresholds |
| Average precision | Summary of the precision–recall ranking curve |
| Calibration | Agreement between predicted probabilities and observed frequencies |

A classifier produces scores; a threshold turns scores into actions. Model
ranking quality and operating-policy quality are related but distinct.

## Worked example: report the minority outcome explicitly

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, classification_report
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=5_000,
    weights=[0.95, 0.05],
    flip_y=0.01,
    random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42
)
model = LogisticRegression(
    class_weight="balanced",
    max_iter=1_000,
).fit(X_train, y_train)
scores = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, scores >= 0.5, digits=3))
print("average precision:", average_precision_score(y_test, scores))
```

The 0.5 threshold is a starting convention, not a law. Select an operating point
using validation data and an explicit cost, capacity, recall, or precision goal.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 41 learner notebook from this guide's **Next
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

## Concept deep dive — rare-class metrics, training interventions, and threshold policy

### The mental model

Class imbalance means the outcome of interest is uncommon, not that the
dataset is automatically unusable. Accuracy can look excellent when a
classifier always predicts the majority class. Start by recording
prevalence and the counts/costs of false negatives and false positives.

Class weights and resampling change the **training objective or training
distribution**. A decision threshold changes how fitted scores become
actions. These are separate choices. Resampling must occur inside each
training fold, and a threshold must be selected on validation evidence,
never final-test labels.

### Worked examples and syntax anatomy

- **`np.bincount(y)` / prevalence:** establishes class support before modeling and must be reported for every evaluation split.
- **`class_weight='balanced'`:** reweights training loss; it does not make the observed population balanced.
- **`precision_recall_curve(y, score)`:** shows threshold trade-offs; selecting a threshold still requires a decision rule and validation boundary.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — expose the majority-class accuracy trap

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.metrics import accuracy_score, recall_score

y_true = np.array([0] * 95 + [1] * 5)
always_negative = np.zeros_like(y_true)
print({
    "prevalence": y_true.mean(),
    "accuracy": accuracy_score(y_true, always_negative),
    "positive_recall": recall_score(y_true, always_negative),
})
assert accuracy_score(y_true, always_negative) == 0.95
assert recall_score(y_true, always_negative) == 0.0
```

**Expected observation:** The classifier is 95% accurate while finding none of the positive cases.

**Assumption to name:** Positive cases are the operational focus; missing all of them is unacceptable.

### Focused example B — choose a threshold from an explicit recall constraint

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.metrics import precision_recall_curve

y_valid = np.array([0, 0, 0, 0, 1, 1, 1, 1])
scores = np.array([0.05, 0.15, 0.35, 0.55, 0.30, 0.50, 0.70, 0.90])
precision, recall, thresholds = precision_recall_curve(y_valid, scores)
candidates = [
    (threshold, p, r)
    for threshold, p, r in zip(thresholds, precision[:-1], recall[:-1])
    if r >= 0.75
]
chosen = max(candidates, key=lambda row: row[1])
print({"threshold": chosen[0], "precision": chosen[1], "recall": chosen[2]})
```

**Expected observation:** The chosen threshold satisfies the stated recall floor and maximizes precision only among eligible validation candidates.

**Assumption to name:** The tiny array is a mechanics demo; a real threshold needs sufficient representative validation support and uncertainty.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define rare-class metrics, training interventions, and threshold policy in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Applying SMOTE or another sampler before the train/test split, which creates related synthetic evidence across boundaries.

**Debug it deliberately:** Trace row IDs through split, sampling, fitting, calibration, threshold selection, and final evaluation; print class counts at each stage.

**Stop condition:** Do not choose a threshold or sampler from final test results or claim synthetic rows add real-world evidence.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Compare `class_weight="balanced"` with a SMOTE strategy.

**Verify:** For task `Compare classweight="balanced" with a SMOTE strategy`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






2. Tune the threshold to maximize minority-class F1.

**Verify:** For task `Tune the threshold to maximize minority-class F1`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then report class support and confusion counts at the chosen threshold and prove the declared operating constraint is satisfied.






3. Plot precision–recall curves and discuss the tradeoff.

**Verify:** For task `Plot precision–recall curves and discuss the tradeoff`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then report class support and confusion counts at the chosen threshold and prove the declared operating constraint is satisfied.







### Progressive hints

1. Resample only `X_train, y_train`. For cross-validation, place SMOTE inside an
   `imblearn.pipeline.Pipeline` so each fold synthesizes from its training rows.
2. Use `precision_recall_curve` on validation scores. Check array lengths
   carefully: thresholds have one fewer element than precision and recall.
3. Plot recall on the x-axis and precision on the y-axis; add class prevalence
   as a simple reference and label average precision.

### Additional mastery practice

Evaluate the minority outcome explicitly and keep resampling, calibration, threshold choice, and entity boundaries inside the correct training scope.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Prevalence-shift reasoning:** Hold sensitivity and specificity fixed while changing event prevalence from 20% to 2%. Predict how precision changes and verify it with Bayes' rule.
   **Progressive hint:** Precision depends on the base rate: TP/(TP+FP). Use a hypothetical population such as 10,000 to make the counts visible.

**Verify:** For task `Prevalence-shift reasoning: Hold sensitivity and specificity fixed while changing event preva...`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then report class support and confusion counts at the chosen threshold and prove the declared operating constraint is satisfied.







5. **Grouped imbalance split:** Create a cross-validation plan for rare outcomes with multiple rows per account. Assert both group separation and acceptable positive support in each fold.
   **Progressive hint:** Use StratifiedGroupKFold when feasible. Print group overlap, positive count, negative count, and prevalence per validation fold.

**Verify:** For task `Grouped imbalance split: Create a cross-validation plan for rare outcomes with multiple rows...`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







6. **Calibration after resampling:** Explain why probabilities from a model trained on oversampled data may not match real prevalence. Design a calibration evaluation using unresampled validation data.
   **Progressive hint:** Oversampling changes the class distribution seen during fitting. Fit/calibrate inside development data and assess reliability on natural prevalence.

**Verify:** For task `Calibration after resampling: Explain why probabilities from a model trained on oversampled d...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- Why can ROC AUC look strong while precision remains poor?
- Which information would you need to choose between false positives and false
  negatives?
- Why is applying SMOTE before splitting a leakage error?
- Does class weighting guarantee calibrated probabilities?

Expected behavior: changing the threshold moves precision and recall in opposite
directions. Class weighting and SMOTE need not produce the same ranking or
calibration.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Accuracy as the only metric | Majority prediction looks successful | Report minority-aware metrics and confusion counts |
| SMOTE before split/CV | Synthetic points include validation information | Resample inside training folds |
| Threshold selected on test labels | Optimistic final metric | Tune on validation, lock, evaluate once |
| Optimizing F1 without costs | Encodes an arbitrary tradeoff | Tie the threshold to operational consequences |
| Ignoring calibration after reweighting | Scores may not represent probabilities | Evaluate/recalibrate on representative data |

Undersampling is cheap but discards evidence. Oversampling preserves rows but
can overfit duplicates or implausible synthetic neighborhoods. Class weights are
simple and often a strong first comparison.

## Next step

- Work in the [Day 41 learner notebook](../notebooks/day41_imbalance_handling.ipynb).
- Then consult the
  [Day 41 solution](../solutions/day41_imbalance_handling/day41_solutions.md).
- Continue to [Day 42 — Unsupervised Learning](day42_unsupervised_kmeans_anomaly.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-41` — Day 41 — Handling Class Imbalance.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize rare-class metrics, training interventions, and threshold policy. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day41_imbalance_handling.md`
- learner artifact: `python/ds-60day/notebooks/day41_imbalance_handling.ipynb`

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
