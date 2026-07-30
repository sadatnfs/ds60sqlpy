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

## Learner exercises and progressive hints

1. Compare `class_weight="balanced"` with a SMOTE strategy.
2. Tune the threshold to maximize minority-class F1.
3. Plot precision–recall curves and discuss the tradeoff.

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
5. **Grouped imbalance split:** Create a cross-validation plan for rare outcomes with multiple rows per account. Assert both group separation and acceptable positive support in each fold.
   **Progressive hint:** Use StratifiedGroupKFold when feasible. Print group overlap, positive count, negative count, and prevalence per validation fold.
6. **Calibration after resampling:** Explain why probabilities from a model trained on oversampled data may not match real prevalence. Design a calibration evaluation using unresampled validation data.
   **Progressive hint:** Oversampling changes the class distribution seen during fitting. Fit/calibrate inside development data and assess reliability on natural prevalence.

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
