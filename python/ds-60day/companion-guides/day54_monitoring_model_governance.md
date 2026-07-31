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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 54 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — monitoring layers, drift signals, delayed labels, and governance decisions

### The mental model

Production monitoring has several layers. Data-quality checks ask
whether inputs are valid. Data drift compares input distributions.
Performance and calibration require outcomes, which may arrive later.
Service telemetry measures availability, latency, errors, and
saturation. One green layer cannot substitute for another.

Population Stability Index (PSI) compares binned reference and current
proportions. Its value depends on binning and sample size and is a
triage signal, not a diagnosis or universal threshold. Governance adds
owners, review cadence, acceptance gates, rollback evidence, privacy,
and an incident path.

### Worked examples and syntax anatomy

- **fixed reference bins:** keep comparison semantics stable; recomputing bins on current data changes the question.
- **`(actual - expected) * log(actual / expected)`:** accumulates PSI contributions after a declared zero-count smoothing policy.
- **monitor → investigate → decide:** separates automated signal detection from causal diagnosis and authorized action.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — calculate PSI with fixed reference quantile bins

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np

reference = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=float)
current = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], dtype=float)
edges = np.quantile(reference, [0, 0.25, 0.5, 0.75, 1.0])
edges[0], edges[-1] = -np.inf, np.inf
expected, _ = np.histogram(reference, bins=edges)
actual, _ = np.histogram(current, bins=edges)
expected = np.clip(expected / expected.sum(), 1e-6, None)
actual = np.clip(actual / actual.sum(), 1e-6, None)
psi = np.sum((actual - expected) * np.log(actual / expected))
print({"edges": edges.tolist(), "psi": float(psi)})
assert psi >= 0
```

**Expected observation:** The shifted current sample produces a positive PSI under bins fixed from the reference sample.

**Assumption to name:** Reference quantiles, smoothing, population, and sample window are documented and remain comparable.

### Focused example B — keep label-available and label-delayed evidence separate

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
monitoring_snapshot = {
    "requests": 10_000,
    "valid_input_rate": 0.998,
    "score_mean": 0.44,
    "outcomes_available": 1_200,
    "labeled_roc_auc": 0.86,
}
label_coverage = (
    monitoring_snapshot["outcomes_available"] / monitoring_snapshot["requests"]
)
print({"label_coverage": label_coverage,
       "performance_estimate": monitoring_snapshot["labeled_roc_auc"]})
assert label_coverage == 0.12
```

**Expected observation:** The performance metric covers only 12% of requests, so label selection and delay must accompany the score.

**Assumption to name:** Available outcomes are representative enough for the scoped estimate; otherwise the metric may be selection-biased.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define monitoring layers, drift signals, delayed labels, and governance decisions in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Treating a PSI threshold as automatic proof of performance degradation or retraining need.

**Debug it deliberately:** Break the alert into data window, reference, bins, counts, slices, label coverage, service changes, and upstream incidents; reproduce the statistic independently.

**Stop condition:** Do not retrain or roll back from one unexplained alert without owner, evidence gate, and impact assessment.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Compute PSI for multiple features or score windows over time.

**Verify:** Practice 1 — monitoring layers, drift signals, delayed labels, and governance decisions — for each named feature/window, print reference/current counts, fixed bin edges, PSI contributions, and total; assert bins/reference remain frozen and independently recompute one total within 1e-12.

2. Build a small pandas/Matplotlib dashboard of weekly AUC and PSI.

**Verify:** Practice 2 — monitoring layers, drift signals, delayed labels, and governance decisions — save a dashboard with weekly AUC and PSI on labeled separate axes, and print the underlying week/support/AUC/PSI table; mark missing-label weeks rather than silently treating them as zero.

3. Draft a governance policy covering roles, approvals, alerts, and rollback.

**Verify:** Practice 3 — monitoring layers, drift signals, delayed labels, and governance decisions — produce a policy table naming model owner, approver, metric/window/threshold, minimum support, alert route, investigation SLA, rollback trigger, artifact ID, and audit evidence; walk one breached alert through named owners and actions.

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

**Verify:** Label-delay analysis — print prediction week, label-available date, immediate-health metrics/support, and matured-cohort AUC/support; assert immature weeks show unavailable performance rather than zero or forward-filled values.

5. **Alert hysteresis:** Design warning and critical thresholds that require persistence or multiple windows, then show how hysteresis prevents alert flapping.
   **Progressive hint:** Use different enter and clear conditions, minimum support, and a cooldown. Preserve raw measurements for audit.

**Verify:** Alert hysteresis — feed a declared metric sequence around warning/critical thresholds, print alert state by window, and assert persistence opens an alert while the lower recovery threshold prevents one-window flapping.

6. **Rollback drill:** Write and rehearse a rollback from model version B to A, including trigger, authority, artifact verification, traffic switch, smoke test, communication, and post-incident evidence.
   **Progressive hint:** A rollback is complete only when the prior artifact, schema, and dependencies remain loadable and the recovery check passes.

**Verify:** Rollback drill — record version-B trigger, authorized actor, verified version-A hash, traffic switch, health/predict smoke results, communication timestamp, and final state; inject a bad rollback artifact and assert the switch stops.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-54` — Day 54 — Monitoring and Model Governance.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize monitoring layers, drift signals, delayed labels, and governance decisions. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day54_monitoring_model_governance.md`
- learner artifact: `python/ds-60day/notebooks/day54_monitoring_model_governance.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-53`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
