# Day 57 — Solutions: Security, Privacy, and Ethics

We build a data classification matrix, compute group metrics for fairness, and provide a model card template.

Contents
- Exercise 1: Data classification matrix
- Exercise 2: Group precision/recall across sensitive groups
- Exercise 3: Model card template

---

Exercise 1 — Data classification matrix
```markdown
| Data class | Examples | Storage | Access | Retention |
|-----------:|----------|---------|--------|-----------|
| Public     | docs, FAQs | public repo | everyone | indefinite |
| Internal   | non‑PII logs | private S3 | team | 1 year |
| Sensitive  | emails, IPs | encrypted S3 | need‑to‑know | 90 days |
| Restricted | PII, health | encrypted vault | least privilege | 30 days |
```
Guidance
- Define classes, storage locations, encryption, access controls, retention periods

---

Exercise 2 — Group metrics
```python
import numpy as np, pandas as pd
from sklearn.metrics import precision_score, recall_score

# Synthetic predictions grouped by sensitive attr 'group'
df = pd.DataFrame({
    'y_true':  np.random.randint(0,2, size=1000),
    'y_pred':  np.random.randint(0,2, size=1000),
    'group':   np.random.choice(['A','B'], size=1000)
})

metrics = (df.groupby('group')
             .apply(lambda g: pd.Series({
                 'precision': precision_score(g.y_true, g.y_pred, zero_division=0),
                 'recall':    recall_score(g.y_true, g.y_pred, zero_division=0),
                 'count':     len(g)
             })))
print(metrics)

# Disparity checks
prec_gap = abs(metrics.loc['A','precision'] - metrics.loc['B','precision'])
rec_gap  = abs(metrics.loc['A','recall'] - metrics.loc['B','recall'])
print({'precision_gap': prec_gap, 'recall_gap': rec_gap})
```
Notes
- For imbalanced data, compare PR curves per group; consider equalized odds/TPR parity goals

---

Exercise 3 — Model card template
```markdown
# Model Card — <model name>

## Overview
- Intended use: ...
- Out of scope: ...
- Owners: ...

## Data
- Sources: ...
- Preprocessing: ...
- Sensitive attributes: handled as ...

## Training
- Algorithms: ...
- Hyperparameters: ...
- Validation: splits, metrics, leakage checks

## Evaluation
- Metrics: overall and per‑group
- Error analysis: common failure modes

## Ethics & Risks
- Bias and fairness analysis summary
- Potential harms and mitigations

## Deployment
- Versioning, monitoring, rollback plan
- Contact for incidents
```
