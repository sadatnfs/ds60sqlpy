# Day 57 — Solutions: Security, Privacy, and Ethics

We build a data classification matrix, compute group metrics for fairness, and provide a model card template.

Contents
- Exercise 1: Data classification matrix
- Exercise 2: Group precision/recall across sensitive groups
- Exercise 3: Model card template

---

Worked reference for Exercise 1 — Data classification matrix
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

Worked reference for Exercise 2 — Group metrics
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

Worked reference for Exercise 3 — Model card template
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

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **allowlist output fields:** starts from data that is necessary rather than trying to detect every sensitive field after collection.
2. **detection → review → action:** treats regex/PII scanners as bounded signals with false positives and false negatives.
3. **group metric + support:** reports numerator/denominator and uncertainty so tiny groups do not create confident-looking claims.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Minimization reduces exposure at the boundary, while support-aware evaluation and governance make remaining risk visible and accountable.

**Useful alternative:** Aggregation, tokenization, differential privacy, or not collecting the field may reduce risk; each changes analytical utility and guarantees.

**Trade-off:** More detailed data can improve diagnostics while increasing re-identification, misuse, access, retention, and breach consequences.

**Edge case to test:** Small groups, intersectional re-identification, proxy variables, deletion across derived artifacts, and model inversion require review beyond regexes.

**Evidence of correctness:** Prove forbidden fields never cross the boundary, test scanner misses/false hits, report group numerators/denominators and uncertainty, and assign owners/retention/incident actions.

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

### Exercise 1 — Original lesson practice

**Prompt:** Build a DataFrame PII scanner covering column names and free text.

**How to reason about it:** A PII scanner should return finding type, safe row identifier, column, and count—not the matched secret. Test false positives, missed formats, Unicode, nulls, and nested/free-text fields.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — data minimization, privacy boundaries, fairness evidence, and accountable controls — run the scanner on named columns and free-text fixtures containing email, phone, clean text, and a deliberate false positive; print row/field/finding type without raw PII and report misses/false hits.

### Exercise 2 — Original lesson practice

**Prompt:** Add a function that masks email addresses and phone numbers in text.

**How to reason about it:** Masking must preserve only the minimum structure needed for the stated purpose and be idempotent. Regex is incomplete, so pair it with minimization, access controls, retention, and review.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — data minimization, privacy boundaries, fairness evidence, and accountable controls — assert masking replaces complete email and phone fixtures with declared placeholders, preserves surrounding non-PII text, is idempotent on a second pass, and handles malformed/boundary strings explicitly.

### Exercise 3 — Original lesson practice

**Prompt:** Simulate subgroup precision and recall for a classifier and compare groups.

**How to reason about it:** Subgroup precision/recall requires support, positive counts, uncertainty, and consistent thresholds. Avoid conclusions for tiny groups and distinguish observed disparity from a causal explanation.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — data minimization, privacy boundaries, fairness evidence, and accountable controls — for each subgroup, print TP/FP/FN, support, precision, recall, and uncertainty or minimum-support warning; verify each rate from its counts and avoid ranking groups with insufficient denominators.

### Exercise 4 — Original lesson practice

**Prompt:** Draft a one-page data-ethics checklist for your project.

**How to reason about it:** An ethics checklist names intended use, excluded use, stakeholders, harms, data rights, fairness evaluation, human oversight, monitoring, appeals, owners, and stop/rollback criteria.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 4 — data minimization, privacy boundaries, fairness evidence, and accountable controls — save a one-page Markdown checklist file with owner and evidence for collection purpose, minimization, consent/legal basis, access, retention/deletion, security, bias evaluation, incident response, and stop/go approval.

### Exercise 5 — Threat modeling

**Prompt:** Create a data-flow diagram for collection, notebook, artifacts, API, logs, and backups. For each boundary, identify asset, actor, threat, control, residual risk, and owner.

**Reasoning before implementation:** Include accidental exposure and insider misuse, not only external attackers. Trace data copies and retention through every stage.

Prioritize threats by credible impact and likelihood, then connect each
control to a verification step: access review, secret scan, encryption check,
retention deletion test, redacted-log test, or incident drill.

A diagram is not a security guarantee. Record residual risk and an accountable
owner; risks beyond the project's authority require escalation rather than a
checkbox marked complete.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Threat modeling — save a data-flow diagram/table covering collection, notebook, artifacts, API, logs, and backups; each boundary must name asset, actor, threat, preventive/detective control, residual risk, owner, and verification test.

### Exercise 6 — Re-identification reasoning

**Prompt:** Generalize a small dataset to satisfy a chosen k-anonymity target, then demonstrate why k-anonymity does not prevent attribute disclosure or attacks using outside information.

**Reasoning before implementation:** Group quasi-identifiers, inspect equivalence-class sizes and sensitive value diversity, and measure utility loss.

k-anonymity limits uniqueness under the selected quasi-identifiers, but a
group whose members all share one sensitive value can still reveal that value.
Unmodeled external data can also re-identify records.

Use the exercise to understand limits, not to certify a dataset as safe.
Privacy review may require stronger techniques, restricted access, synthetic
data, or differential privacy with an explicit threat model and privacy budget.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Re-identification reasoning — print equivalence-class sizes proving the chosen k target, then construct a homogeneous sensitive-attribute class and an outside-information linkage example that still discloses information.

### Exercise 7 — Fairness uncertainty

**Prompt:** Bootstrap subgroup precision and recall, show confidence intervals and support, and compare a gap with a ratio. Explain what to do when one group's denominator is nearly zero.

**Reasoning before implementation:** Resample at the independent entity level when rows repeat. Undefined metrics should remain undefined rather than being forced to zero.

Report the distribution of gaps/ratios, not only point estimates. Wide
intervals signal insufficient evidence, which may require more representative
data or a safer deployment constraint. A zero predicted-positive denominator
makes precision undefined and must be surfaced.

Metric parity choices can conflict and depend on base rates and harm. Select
the monitored criterion with affected stakeholders and domain/legal review,
not by whichever metric looks most favorable.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Fairness uncertainty — with declared bootstrap seed/resamples, print subgroup TP/FP/FN, support, precision/recall intervals, gap and ratio; when a denominator is near zero, return an insufficient-support warning instead of an unstable rank.

### Exercise 8 — Incident response

**Prompt:** Simulate discovering raw emails in a committed notebook output. Write the containment, notification, credential review, history cleanup decision, verification, and prevention steps.

**Reasoning before implementation:** Preserve a restricted incident record, stop further sharing, and assume copied history may exist. Redaction from the latest commit alone is insufficient.

Follow the organization's incident process and involve repository/security
owners before rewriting shared history. Remove outputs from current artifacts,
rotate exposed credentials if any, assess clones/releases/caches, and notify
affected parties according to policy.

Add preventive controls: clean-output notebook validation, secret/PII scans,
synthetic fixtures, `.gitignore`, review checks, and least-privilege data
access. Do not reproduce the sensitive value in tickets or logs.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Incident response — produce a timestamped incident record with containment, notification owner, credential assessment, history-rewrite decision, post-clean scan/hash, and prevention test; verify the raw email sentinel no longer appears in current artifacts.
