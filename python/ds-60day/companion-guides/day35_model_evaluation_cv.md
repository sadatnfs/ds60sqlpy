# Day 35 — Model Evaluation and Cross-Validation (Companion Guide)

## Learning objectives
- Choose appropriate metrics for regression/classification
- Use K-fold, StratifiedKFold, and TimeSeriesSplit
- Understand ROC/PR curves, calibration, and variance

## Why this matters
Correct evaluation choices align models to business goals and avoid misleading results.

## Core concepts and examples
### Metrics
```python
from sklearn.metrics import mean_squared_error, r2_score, roc_auc_score, average_precision_score
```

### Cross-validation
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
scores = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc')
```

### ROC and PR
```python
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay
RocCurveDisplay.from_estimator(clf, X_test, y_test)
PrecisionRecallDisplay.from_estimator(clf, X_test, y_test)
```

## Common pitfalls
- Using accuracy on imbalanced data; prefer AUC/PR/recall@k
- Data leakage across folds (e.g., grouping or time leakage)
- Reporting mean without variance; include std or CI

## Practice exercises
1) Compare metrics across models with CV
2) Plot ROC/PR and choose an operating threshold
3) Use TimeSeriesSplit for temporal data

## Further reading
- Model evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html
