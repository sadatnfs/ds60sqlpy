# Day 54 — Monitoring and Model Governance (Companion Guide)

## Learning objectives
- Monitor data quality, drift, and performance in production
- Log predictions with features/metadata; design feedback loops
- Understand governance: lineage, approvals, and auditability

## Why this matters
Models live in dynamic environments. Monitoring and governance ensure safety, reliability, and compliance.

## Core concepts and examples
- Data quality checks: schema validation, ranges, missingness, anomalies
- Drift detection: PSI, KL divergence, population stability indices
- Performance tracking: delayed ground truth, windowed metrics
- Governance: versioning models/data/code; approvals; reproducible builds

## Example (sketch)
```python
# compute PSI between train and prod feature distributions
import numpy as np
# binning and PSI function omitted for brevity
```

## Common pitfalls
- No ground truth pipeline; performance unknown
- Silent schema drift breaking assumptions
- Storing PII without proper controls and retention policies

## Practice exercises
1) Implement and visualize drift metrics for two datasets
2) Design a logging schema for online predictions
3) Propose an approval flow for pushing a new model version

## Further reading
- EvidentlyAI: https://evidentlyai.com
- Data governance: https://www.mondelezinternational.com/-/media/Mondelez/Files/governance.pdf (conceptual)
