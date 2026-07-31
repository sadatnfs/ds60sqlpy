# Day 35 — Solutions: Model Evaluation and Cross-Validation

We evaluate models with appropriate metrics, perform k-fold CV, and discuss bias/variance and leakage.

Contents
- Exercise 1: Compare metrics (accuracy, f1, roc_auc) under CV
- Exercise 2: Compare 5-fold vs 10-fold variability
- Exercise 3: Show how pipelines help prevent leakage

---

Exercise 1 — Metrics with CV
```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

X, y = load_breast_cancer(return_X_y=True)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

clf = Pipeline([
    ('sc', StandardScaler()),
    ('lr', LogisticRegression(max_iter=1000, solver='lbfgs'))
])

scores_acc = cross_val_score(clf, X, y, cv=cv, scoring='accuracy')
scores_f1  = cross_val_score(clf, X, y, cv=cv, scoring='f1')
scores_auc = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc')

{
    'acc_mean': scores_acc.mean(), 'acc_std': scores_acc.std(),
    'f1_mean': scores_f1.mean(),   'f1_std': scores_f1.std(),
    'auc_mean': scores_auc.mean(), 'auc_std': scores_auc.std(),
}
```
Notes
- Use StratifiedKFold for classification to preserve class ratios
- Report mean and variability (std or CI)

---

Exercise 2 — 5-fold vs 10-fold
```python
cv5  = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
cv10 = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
auc5  = cross_val_score(clf, X, y, cv=cv5,  scoring='roc_auc')
auc10 = cross_val_score(clf, X, y, cv=cv10, scoring='roc_auc')
{'auc5_mean': auc5.mean(), 'auc5_std': auc5.std(), 'auc10_mean': auc10.mean(), 'auc10_std': auc10.std()}
```
Observation
- 10-fold gives more train data per fold (less bias), but more variance across folds; compare stds

---

Exercise 3 — Leakage and pipelines
- Scaling and other preprocessing must be fit within each CV fold to avoid peeking at test fold
- Pipelines ensure transform.fit is applied only on training split; transforms then apply to held-out split via transform

Takeaways
- Choose metrics aligned with the business goal (e.g., recall@k for safety-critical)
- Always cross-validate with proper fold type (stratified vs time series)
- Use pipelines to control leakage and keep code reproducible

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`confusion_matrix(y_true, y_pred)`:** returns outcome counts at the selected threshold; inspect label order before unpacking.
2. **`cross_validate(estimator, X, y, cv=..., scoring=...)`:** fits a fresh estimator per fold and can report multiple metrics and timing.
3. **splitter objects:** encode random, stratified, grouped, or temporal assumptions; `cv=5` is not a universal design.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Decision-aligned metrics and structure-aware resampling make the reported estimate answer the intended future-use question.

**Useful alternative:** A fixed holdout is simpler and valuable for final confirmation; repeated or nested CV estimates more of the selection procedure at higher cost.

**Trade-off:** More folds train on more data per fold but increase compute and correlation between fold estimates.

**Edge case to test:** A fold with one class, a group that dominates the dataset, or time leakage can make a nominal score undefined or misleading.

**Evidence of correctness:** Recompute metrics from outcome counts, prove split-unit disjointness, report every fold score plus variability, and preserve a separate final-evaluation boundary.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Reasoning notes for original Exercise 1

**Prompt:** Evaluate the pipeline with `accuracy`, `f1`, and `roc_auc`.

**How to reason about it:** Accuracy and F1 use thresholded labels, while ROC AUC uses ranking scores. Keep folds identical and report class prevalence so readers can understand why the metrics may disagree.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Evaluate the pipeline with accuracy, f1, and rocauc`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Reasoning notes for original Exercise 2

**Prompt:** Compare the variability from 5-fold and 10-fold cross-validation.

**How to reason about it:** Five and ten folds trade training-set size against compute and fold variance. Compare the paired fold procedure across repeated seeds rather than announcing a universal winner from one split.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Compare the variability from 5-fold and 10-fold cross-validation`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 3

**Prompt:** Explain leakage risks and how placing preprocessing in a pipeline helps.

**How to reason about it:** Any transform learned before cross-validation leaks validation-fold information. A pipeline causes preprocessing to be cloned and refit inside every fold, but it cannot repair leakage already baked into features.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Explain leakage risks and how placing preprocessing in a pipeline helps`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Exercise 4 — Threshold analysis

**Prompt:** Using one fixed validation score vector, compare confusion matrices at thresholds 0.2, 0.5, and 0.8. Explain which errors increase as the threshold rises and why ROC AUC stays unchanged.

**Reasoning before implementation:** A higher positive threshold generally reduces predicted positives: false positives fall while false negatives rise. Ranking scores do not change.

Build the matrix with an explicit label order such as `[0, 1]` and record
support beside rates. Threshold selection is a policy decision; choose it on
validation data using error costs or a documented constraint, then evaluate
that frozen threshold once on the final holdout.

ROC AUC is unchanged because it considers ranking across all possible
thresholds. Precision, recall, F1, and the confusion matrix do change because
they consume the thresholded labels.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Using one fixed validation score vector, compare confusion matrices at thresholds 0.2, 0.5, a...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Exercise 5 — Grouped resampling

**Prompt:** Design cross-validation for repeated measurements from the same patient or customer. Demonstrate how ordinary StratifiedKFold can place one entity in both training and validation.

**Reasoning before implementation:** Use `StratifiedGroupKFold` when both label balance and entity separation matter; assert that train and validation group sets are disjoint.

Rows from one entity are correlated, so random row-level folds can let the
model recognize entity-specific patterns rather than generalize to new
entities.

```python
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

X = np.arange(80, dtype=float).reshape(40, 2)
y = np.tile([0, 1], 20)
entity_ids = np.repeat(np.arange(20), 2)
splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=35)
for train_index, valid_index in splitter.split(X, y, groups=entity_ids):
    train_groups = set(entity_ids[train_index])
    valid_groups = set(entity_ids[valid_index])
    assert train_groups.isdisjoint(valid_groups)
```

If deployment predicts future rows for already-known entities, a different
split may be appropriate; align the split with that real decision explicitly.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Design cross-validation for repeated measurements from the same patient or customer. Demonstr...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 6 — Selection-bias debugging

**Prompt:** Explain why reporting `GridSearchCV.best_score_` as final performance is optimistic. Sketch a nested cross-validation design and distinguish it from out-of-fold predictions for one fixed model.

**Reasoning before implementation:** The same inner folds both select and report the best candidate. Nested CV puts the complete search inside an outer held-out fold.

`best_score_` is the highest noisy estimate among tried configurations, so
selection favors candidates that benefited from sampling noise. In nested CV:

1. the inner splitter selects hyperparameters using only the outer-training rows;
2. the selected pipeline predicts the untouched outer-validation rows;
3. outer scores summarize the complete model-selection procedure.

`cross_val_predict` can generate out-of-fold predictions for a fixed estimator,
but it is not automatically nested. Passing the entire search object to the
outer loop is what repeats selection honestly.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Explain why reporting GridSearchCV.bestscore as final performance is optimistic. Sketch a nes...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
