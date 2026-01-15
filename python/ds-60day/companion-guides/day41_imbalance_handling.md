# Day 41 — Handling Class Imbalance (Companion Guide)

## Learning objectives
- Diagnose imbalance and select metrics accordingly
- Use class weights, under/over-sampling, and SMOTE variants
- Adjust decision thresholds and evaluate cost-sensitive performance

## Why this matters
Imbalanced labels are common; naive accuracy can be misleading. You must optimize for recall/precision tradeoffs.

## Core concepts and examples
### Class weights
```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=0)
```

### Resampling (imblearn)
```python
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
pipe = Pipeline([
    ('pre', preprocessor),
    ('smote', SMOTE(random_state=0)),
    ('model', LogisticRegression(max_iter=1000))
])
```

### Threshold tuning
```python
from sklearn.metrics import precision_recall_curve
probs = clf.predict_proba(X_valid)[:,1]
prec, rec, thr = precision_recall_curve(y_valid, probs)
```

## Common pitfalls
- Performing resampling before train/test split (leakage)
- Evaluating with accuracy only; prefer PR AUC, recall@k, F-beta
- SMOTE on high-dimensional sparse features; consider alternatives

## Practice exercises
1) Compare class_weight vs SMOTE in a pipeline
2) Plot PR curve and choose threshold for desired recall
3) Report confusion matrix at multiple thresholds

## Further reading
- imbalanced-learn: https://imbalanced-learn.org
