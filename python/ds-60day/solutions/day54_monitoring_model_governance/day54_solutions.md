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

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **fixed reference bins:** keep comparison semantics stable; recomputing bins on current data changes the question.
2. **`(actual - expected) * log(actual / expected)`:** accumulates PSI contributions after a declared zero-count smoothing policy.
3. **monitor → investigate → decide:** separates automated signal detection from causal diagnosis and authorized action.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Layered monitoring identifies which contract changed, while governance converts evidence into accountable and reversible decisions.

**Useful alternative:** Kolmogorov-Smirnov, Jensen-Shannon, calibration, or model-based drift checks answer different questions; none removes the need for labels and domain review.

**Trade-off:** Sensitive alerts detect changes sooner but increase false alarms; long windows stabilize metrics while delaying response.

**Edge case to test:** Zero-count bins, tiny slices, delayed/missing labels, seasonality, upstream schema changes, and changed model versions can create misleading trends.

**Evidence of correctness:** Freeze reference/bins and recompute PSI, report counts/windows/slices/label coverage, connect alerts to owners/actions, and rehearse rollback with artifact evidence.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Reasoning notes for original Exercise 1

**Prompt:** Compute PSI for multiple features or score windows over time.

**How to reason about it:** Freeze reference bins, include support, and test no shift plus controlled mean/variance shifts. PSI depends on binning and is a heuristic signal, not proof of performance degradation.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Compute PSI for multiple features or score windows over time`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then show the formula or intermediate quantities and check the final value independently rather than trusting one library call.








### Reasoning notes for original Exercise 2

**Prompt:** Build a small pandas/Matplotlib dashboard of weekly AUC and PSI.

**How to reason about it:** A weekly dashboard should retain model/data version, score volume, label coverage, AUC uncertainty, PSI, and missingness. Mark delayed labels rather than inventing or forward-filling performance.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Build a small pandas/Matplotlib dashboard of weekly AUC and PSI`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 3

**Prompt:** Draft a governance policy covering roles, approvals, alerts, and rollback.

**How to reason about it:** Every governance threshold needs an owner, evidence source, review clock, action, escalation, and recovery test. Separate automated alerts from human approval for promotion/rollback.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Draft a governance policy covering roles, approvals, alerts, and rollback`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Exercise 4 — Label-delay analysis

**Prompt:** Simulate labels arriving 14–30 days after predictions. Build separate views for immediate input/score health and matured performance cohorts.

**Reasoning before implementation:** Join outcomes by stable prediction ID and evaluate only cohorts whose label window has matured; report label coverage and censoring.

Current-week AUC is not available when outcomes arrive later. Operational
signals such as schema failures, missingness, score distribution, latency, and
volume can be monitored immediately. Performance metrics belong to matured
prediction cohorts with explicit cutoff dates.

Late or selectively missing labels can bias results. Compare coverage across
slices and investigate the label process rather than treating unlabeled rows
as negatives.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Simulate labels arriving 14–30 days after predictions. Build separate views for immediate inp...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.








### Exercise 5 — Alert hysteresis

**Prompt:** Design warning and critical thresholds that require persistence or multiple windows, then show how hysteresis prevents alert flapping.

**Reasoning before implementation:** Use different enter and clear conditions, minimum support, and a cooldown. Preserve raw measurements for audit.

For example, enter warning after PSI exceeds a reviewed threshold for two
consecutive supported windows, but clear only after it stays below a lower
threshold for two windows. Critical conditions can bypass the delay when a
hard safety constraint fails.

Thresholds are policy, not universal PSI constants. Validate them on historical
incidents and false-alarm cost, assign ownership, and version changes.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Design warning and critical thresholds that require persistence or multiple windows, then sho...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 6 — Rollback drill

**Prompt:** Write and rehearse a rollback from model version B to A, including trigger, authority, artifact verification, traffic switch, smoke test, communication, and post-incident evidence.

**Reasoning before implementation:** A rollback is complete only when the prior artifact, schema, and dependencies remain loadable and the recovery check passes.

Run the drill in a disposable/local environment and time each step. Verify
artifact hashes and input compatibility before switching. After rollback,
confirm health, prediction shape, representative fixture outputs, and
monitoring recovery.

Keep version B and incident evidence for investigation; do not overwrite or
delete the failed artifact as part of the emergency path.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Write and rehearse a rollback from model version B to A, including trigger, authority, artifa...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
