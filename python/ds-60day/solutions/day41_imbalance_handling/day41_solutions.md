# Day 41 — Solutions: Handling Class Imbalance

We diagnose imbalance, pick appropriate metrics, try class weighting and resampling, and tune the decision threshold for the minority class. We also plot PR curves for a clearer picture than ROC under imbalance.

Contents
- Exercise 1: Compare class_weight vs SMOTE strategies
- Exercise 2: Tune threshold to maximize F1 for the minority class
- Exercise 3: Plot PR curves and discuss

---

Setup
```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, roc_auc_score, 
                             precision_recall_curve, average_precision_score, f1_score)
from sklearn.linear_model import LogisticRegression
import numpy as np
import matplotlib.pyplot as plt

X, y = make_classification(n_samples=5000, weights=[0.95, 0.05],
                           flip_y=0.01, random_state=42)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
```

Exercise 1 — class_weight vs SMOTE
```python
# Class weighting
clf_bal = LogisticRegression(max_iter=1000, class_weight='balanced', n_jobs=-1)
clf_bal.fit(Xtr, ytr)
proba_bal = clf_bal.predict_proba(Xte)[:,1]
yhat_bal  = (proba_bal >= 0.5).astype(int)

print('Balanced weights — report at 0.5 threshold:')
print(classification_report(yte, yhat_bal, digits=3))
print({'roc_auc': roc_auc_score(yte, proba_bal),
       'avg_precision': average_precision_score(yte, proba_bal)})

# Optional: SMOTE
try:
    from imblearn.over_sampling import SMOTE
    sm = SMOTE(random_state=42)
    Xtr_sm, ytr_sm = sm.fit_resample(Xtr, ytr)
    clf_sm = LogisticRegression(max_iter=1000, n_jobs=-1).fit(Xtr_sm, ytr_sm)
    proba_sm = clf_sm.predict_proba(Xte)[:,1]
    yhat_sm  = (proba_sm >= 0.5).astype(int)
    print('SMOTE — report at 0.5 threshold:')
    print(classification_report(yte, yhat_sm, digits=3))
    print({'roc_auc': roc_auc_score(yte, proba_sm),
           'avg_precision': average_precision_score(yte, proba_sm)})
except Exception as e:
    print('SMOTE unavailable — pip install imbalanced-learn to enable.\n', e)
```
Notes
- class_weight='balanced' reweights the loss; very cheap and often effective
- SMOTE synthesizes minority samples; use with care (only on training folds)

---

Exercise 2 — Threshold tuning for minority F1
```python
def best_f1_threshold(y_true, proba):
    prec, rec, th = precision_recall_curve(y_true, proba)
    # precision_recall_curve returns thresholds for all but first point
    th = np.r_[0.0, th]  # align lengths
    f1s = 2 * prec * rec / (prec + rec + 1e-12)
    i = np.nanargmax(f1s)
    return th[i], f1s[i], prec[i], rec[i]

th_star, f1_star, p_star, r_star = best_f1_threshold(yte, proba_bal)
print({'best_threshold': float(th_star), 'best_f1': float(f1_star),
       'precision': float(p_star), 'recall': float(r_star)})

# Apply tuned threshold
yhat_star = (proba_bal >= th_star).astype(int)
print(classification_report(yte, yhat_star, digits=3))
```
Tips
- Pick a threshold using PR-based criteria when positive class is rare
- Use cross-validation to choose threshold robustly, then evaluate on held-out data

---

Exercise 3 — PR curve
```python
prec, rec, _ = precision_recall_curve(yte, proba_bal)
ap = average_precision_score(yte, proba_bal)
plt.plot(rec, prec, label=f'LogReg (AP={ap:.3f})')
plt.xlabel('Recall'); plt.ylabel('Precision'); plt.title('Precision–Recall curve')
plt.legend(); plt.tight_layout(); plt.show()
```
Notes
- PR curves reflect performance on the positive class directly; small AP indicates difficulty under imbalance
- Compare class_weight vs SMOTE curves to decide which to deploy

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Compare `class_weight="balanced"` with a SMOTE strategy.

**How to reason about it:** Class weights change the loss; SMOTE changes the training sample. Resample only within each training fold and compare precision, recall, average precision, calibration, and runtime on untouched validation rows.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Tune the threshold to maximize minority-class F1.

**How to reason about it:** Threshold optimization consumes validation data. Align the shorter threshold array from `precision_recall_curve`, state the target metric or constraint, and freeze the threshold before final testing.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Plot precision–recall curves and discuss the tradeoff.

**How to reason about it:** A precision-recall curve should include class prevalence and support. Use model scores rather than hard labels and do not compare curves drawn from different evaluation populations without labeling that difference.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 4 — Prevalence-shift reasoning

**Prompt:** Hold sensitivity and specificity fixed while changing event prevalence from 20% to 2%. Predict how precision changes and verify it with Bayes' rule.

**Reasoning before implementation:** Precision depends on the base rate: TP/(TP+FP). Use a hypothetical population such as 10,000 to make the counts visible.

With lower prevalence, true positives become rarer while false positives from
the much larger negative population can dominate. For sensitivity `s`,
specificity `c`, and prevalence `p`:

`precision = s*p / (s*p + (1-c)*(1-p))`.

This is why a threshold tuned on a balanced development sample may not deliver
the expected precision after deployment. Re-estimate operating metrics for the
deployment base rate and monitor it over time.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Grouped imbalance split

**Prompt:** Create a cross-validation plan for rare outcomes with multiple rows per account. Assert both group separation and acceptable positive support in each fold.

**Reasoning before implementation:** Use StratifiedGroupKFold when feasible. Print group overlap, positive count, negative count, and prevalence per validation fold.

No splitter can create positives that do not exist across enough independent
groups. Before modeling, count positive groups and reduce the fold count when
necessary. Then assert group disjointness and report fold support.

If a fold has zero positives, recall and average precision are not meaningful;
do not replace that condition with a reassuring zero. Consider repeated
grouped holdouts or a time-aware group design that matches deployment.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Calibration after resampling

**Prompt:** Explain why probabilities from a model trained on oversampled data may not match real prevalence. Design a calibration evaluation using unresampled validation data.

**Reasoning before implementation:** Oversampling changes the class distribution seen during fitting. Fit/calibrate inside development data and assess reliability on natural prevalence.

Oversampling is a training intervention; it must never be applied to validation
or test rows. Evaluate reliability diagrams, Brier score, and log loss on
unresampled data. If calibration is needed, use a separate calibration split or
cross-validated calibrator after the resampling pipeline has been selected.

Also compare ranking metrics: calibration can improve probability meaning
without changing rank-based AUC very much.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
