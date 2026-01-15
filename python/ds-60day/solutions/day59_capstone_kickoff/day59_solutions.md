# Day 59 — Solutions: Capstone Kickoff

We provide concrete templates and examples for scope, metrics, data access, baseline, risks, and milestones.

Contents
- Exercise 1: Problem statement and hypotheses
- Exercise 2: Data sources and access plan
- Exercise 3: Baseline metric, risks, milestones

---

Exercise 1 — Problem and hypotheses (template)
```markdown
# Problem Statement
We aim to predict <target> for <users/stakeholders> to achieve <business value>.

## Hypotheses
- H1: Feature A (e.g., last_login) is predictive of churn.
- H2: Text sentiment from tickets correlates with upsell.
- H3: Seasonality drives demand; including holidays improves forecast.

## Success Metrics
- Primary: AUC ≥ 0.80 on holdout within ±2% over 4 weeks
- Secondary: Calibration error ≤ 0.02, latency ≤ 50ms P95
```

Exercise 2 — Data sources and contracts
```markdown
## Sources
- Warehouse table analytics.users_daily (owner: data-eng)
- CRM API /tickets (owner: ops)

## Contracts
- Schema, freshness (daily by 02:00 UTC), null rate < 1%
- Access: request via JIRA SEC‑123; principle of least privilege
```

Exercise 3 — Baseline, risks, milestones
```markdown
## Baseline
- Heuristic: last_30d_activity>0 → non‑churner; baseline AUC ≈ 0.62

## Risks
- Data leakage from future‑derived features
- Nonstationarity; quarterly product changes
- PII handling for GDPR/CCPA

## Milestones
- Week 1: Data audit + baseline
- Week 2: Feature engineering + model v1
- Week 3: Evaluation + error analysis
- Week 4: Packaging + demo + report
```
