# Day 54 — Solutions: Monitoring and Model Governance

We compute simple drift metrics (PSI), design a logging schema, and outline an approval flow.

Contents
- Exercise 1: Implement and visualize drift metrics (PSI)
- Exercise 2: Design a logging schema for online predictions
- Exercise 3: Propose an approval flow for new model versions

---

Exercise 1 — PSI implementation
```python
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

# PSI between reference (train) and current (prod) for one feature

def psi(ref: pd.Series, cur: pd.Series, bins=10):
    ref = ref.dropna(); cur = cur.dropna()
    edges = np.quantile(ref, np.linspace(0,1,bins+1))
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts = np.histogram(ref, bins=edges)[0]
    cur_counts = np.histogram(cur, bins=edges)[0]
    ref_pct = np.clip(ref_counts / ref_counts.sum(), 1e-6, 1)
    cur_pct = np.clip(cur_counts / cur_counts.sum(), 1e-6, 1)
    return float(np.sum((ref_pct - cur_pct) * np.log(ref_pct/cur_pct)))

# Demo
data_train = pd.Series(np.random.normal(0,1, size=10_000), name='feature')
data_prod  = pd.Series(np.random.normal(0.5,1.2, size=5_000), name='feature')
print({'PSI_feature': psi(data_train, data_prod)})

# Visualize
def plot_dist(a,b,label_a='ref',label_b='cur'):
    plt.hist(a, bins=40, alpha=0.6, label=label_a, density=True)
    plt.hist(b, bins=40, alpha=0.6, label=label_b, density=True)
    plt.legend(); plt.title('Feature distribution'); plt.show()

plot_dist(data_train, data_prod)
```
Notes
- PSI > 0.25 often indicates major shift (rule of thumb); combine with KS tests
- Compute per‑feature PSI and rank to prioritize checks

---

Exercise 2 — Logging schema
```json
{
  "timestamp": "2024-01-01T12:34:56Z",
  "model": {"name": "rf-churn", "version": "2.1.0", "git_sha": "abc123"},
  "request_id": "uuid-...",
  "features": {"age": 42, "tenure": 12, "plan": "pro"},
  "prediction": {"score": 0.73, "label": 1, "threshold": 0.6},
  "metadata": {"latency_ms": 12.4, "node": "pod-1"}
}
```
Guidance
- Include model identity (name, version, git SHA), request id, input features (after schema validation), prediction, threshold, and latency
- Ensure PII minimization; hash or drop sensitive fields
- Store to an append‑only sink (e.g., Kafka → data lake) with retention

---

Exercise 3 — Approval flow
- PR merges to main trigger CI: unit tests, data contract tests, reproducible training
- Register candidate model to Registry as Staging; run shadow deployment A/B tests
- Approval gate requires: model card, fairness metrics, governance checklist
- Promote to Production with change record; set up monitoring alerts and rollback plan
