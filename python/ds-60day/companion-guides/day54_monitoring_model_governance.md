# Day 54 — Monitoring and Model Governance

**Lesson ID:** `python-54` · **Level:** advanced · **Dependencies:** `data` · **Network:** offline

Deployment changes the question from “How did the model score once?” to “Is the
whole decision system still behaving acceptably?” Monitoring provides evidence;
governance assigns ownership and defines what happens next.

## Learning objectives

By the end of the lesson, you can:

- distinguish data quality, drift, performance, calibration, and service health;
- calculate and trend a simple Population Stability Index (PSI);
- design privacy-aware prediction logs;
- define owners, review gates, alerts, and rollback evidence; and
- explain why a drift statistic is a signal rather than a diagnosis.

## Prerequisites

- Complete `python-53` (MLflow tracking).
- Recall held-out performance, data schemas, and artifact versioning.
- Be prepared to state a monitoring window and reference population.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Data drift | Input distribution changes |
| Concept drift | Relationship between inputs and target changes |
| Performance drift | Decision metric changes once delayed labels arrive |
| Calibration drift | Predicted probabilities no longer match observed rates |
| PSI | Binned comparison of reference and current proportions |
| Service-level indicator | Measured behavior such as latency or error rate |
| Alert threshold | Declared condition triggering investigation/action |
| Rollback | Restoring a known version when risk exceeds tolerance |

Monitoring layers answer different questions: **Is data valid? Has it changed?
Does the model still work? Is the service healthy? Is impact acceptable across
groups?**

## Worked example: treat PSI as a defined calculation

```python
import numpy as np


def psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    edges = np.quantile(reference, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    reference_counts = np.histogram(reference, bins=edges)[0]
    current_counts = np.histogram(current, bins=edges)[0]
    reference_rate = np.clip(reference_counts / reference_counts.sum(), 1e-6, 1)
    current_rate = np.clip(current_counts / current_counts.sum(), 1e-6, 1)
    return float(
        np.sum(
            (current_rate - reference_rate)
            * np.log(current_rate / reference_rate)
        )
    )
```

Quantile edges are learned from the reference and extended to infinity so
current out-of-range observations are counted. Duplicated quantiles, missing
values, and tiny samples need explicit handling in real code.

## Learner exercises and progressive hints

1. Compute PSI for multiple features or score windows over time.
2. Build a small pandas/Matplotlib dashboard of weekly AUC and PSI.
3. Draft a governance policy covering roles, approvals, alerts, and rollback.

### Progressive hints

1. Freeze each feature's reference bin edges and record sample counts beside PSI.
   Test “no shift,” mean shift, and variance shift.
2. Use one row per week with observation count, label coverage, AUC, PSI, and
   model version. Mark missing/delayed labels instead of filling fake metrics.
3. For every threshold, name an owner, review clock, evidence source, action,
   escalation path, and recovery test.

### Additional mastery practice

Design monitoring around observable data, delayed truth, action thresholds, ownership, and rehearsed recovery—not dashboards that merely display numbers.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Label-delay analysis:** Simulate labels arriving 14–30 days after predictions. Build separate views for immediate input/score health and matured performance cohorts.
   **Progressive hint:** Join outcomes by stable prediction ID and evaluate only cohorts whose label window has matured; report label coverage and censoring.
5. **Alert hysteresis:** Design warning and critical thresholds that require persistence or multiple windows, then show how hysteresis prevents alert flapping.
   **Progressive hint:** Use different enter and clear conditions, minimum support, and a cooldown. Preserve raw measurements for audit.
6. **Rollback drill:** Write and rehearse a rollback from model version B to A, including trigger, authority, artifact verification, traffic switch, smoke test, communication, and post-incident evidence.
   **Progressive hint:** A rollback is complete only when the prior artifact, schema, and dependencies remain loadable and the recovery check passes.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Can input drift occur without performance degradation?
- Why can performance degrade without detectable marginal feature drift?
- What happens to AUC monitoring before labels arrive?
- Which raw fields should not be copied into prediction logs?
- What evidence proves a rollback restored acceptable behavior?

Expected behavior: the notebook's simulated second score distribution has lower
separability and a nonzero PSI. Exact values depend on bins and data; no PSI
number alone mandates a universal action.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Universal PSI threshold copied from a blog | Context-free alerts | Calibrate thresholds with historical variation and risk |
| Current values outside reference range ignored | Drift understated | Use open-ended edge bins |
| AUC calculated on partial labels | Selection bias | Track label coverage/delay |
| Raw features logged by default | Privacy/security exposure | Minimize, tokenize, aggregate, and retain intentionally |
| Alert without owner/runbook | Noise with no action | Bind alerts to decision procedures |
| Monitoring only global averages | Subgroup harm is hidden | Track relevant cohorts with sample-size safeguards |

Monitoring every feature increases cost and false alarms. Prioritize data
contracts, important features, decision outcomes, critical subgroups, and system
health; document what is intentionally not monitored.

## Next step

- Work in the [Day 54 learner notebook](../notebooks/day54_monitoring_model_governance.ipynb).
- Then review the
  [Day 54 solution](../solutions/day54_monitoring_model_governance/day54_solutions.md).
- Continue to [Day 55 — Docker](day55_apis_containerization_docker.md).
