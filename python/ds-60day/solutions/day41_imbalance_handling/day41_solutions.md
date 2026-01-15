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
