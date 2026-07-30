# Resampling, experiments, and causal boundaries

**Stable ID:** `python-stats-01`

**Level:** advanced

**Estimated time:** 240–300 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-32`
- Python Days 1–32
- Means, variance, confidence intervals, hypothesis tests, and p-values
- SQL or pandas grouping is helpful but not required

All calculations use the standard library and the tracked
[`experiment_outcomes.csv`](../fixtures/data/experiment_outcomes.csv). Random
resampling uses explicit local seeds.

## Learning objectives

You will be able to:

1. Compute and interpret an unstandardized and standardized effect.
2. Build a seeded bootstrap interval for a difference in means.
3. Run an exact or Monte Carlo permutation test.
4. Estimate per-arm sample size from effect, alpha, and power.
5. Apply Holm multiple-comparison adjustment.
6. Check baseline allocation balance.
7. Explain why unplanned sequential peeking raises false-positive risk.
8. Write an A/B plan with assignment unit and primary metric.
9. Bound causal claims by design, attrition, and implementation.

## Vocabulary and concepts

- **Estimand:** exact quantity the experiment seeks to estimate.
- **Effect size:** magnitude of a difference, raw or standardized.
- **Bootstrap:** resampling observed units with replacement.
- **Permutation test:** comparing assignment rearrangements under a null.
- **Exchangeability:** condition that makes a resampling scheme meaningful.
- **Power:** probability of rejecting the null for a specified true effect.
- **Alpha:** planned false-positive probability for a test family.
- **Family-wise error:** probability of one or more false positives in a family.
- **Holm procedure:** sequential p-value adjustment controlling family-wise
  error.
- **Assignment unit:** entity randomized, such as user, account, or site.
- **Randomization check:** pre-outcome check for major assignment imbalance or
  implementation failure.
- **Sequential peeking:** repeatedly testing accumulating outcomes without a
  planned stopping rule.
- **Causal claim:** claim about what assignment changed, requiring design
  assumptions beyond a small p-value.

## Worked example / walkthrough

Run the learner file and predict the treatment-minus-control mean difference.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_stats_01_resampling_experiments.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_stats_01_resampling_experiments.py
```

The fixture has eight completed units per arm, identical baseline score
distributions, and treatment outcomes shifted upward by two. It is deliberately
small enough for all `C(16, 8) = 12,870` assignments to be enumerated.

The solution reports the estimate, standardized effect, bootstrap interval,
exact permutation p-value, approximate sample plan, and adjusted p-values.
None alone establishes that a real-world causal design was implemented.

## Exercises

### 1. Define the experiment before analysis

Write an `ExperimentPlan` containing:

- assignment unit,
- one primary metric and window,
- minimum sample per arm,
- alpha,
- intended analysis,
- planned stopping/looks, and
- missing-outcome handling.

Do this before computing outcomes.

### 2. Complete standardized effect

Use the pooled sample standard deviation. Reject groups smaller than two and
zero pooled variance. Explain raw units and standardized units side by side.

### 3. Bootstrap the difference

Resample each arm independently with replacement, compute 2,000 differences,
sort them, and select percentile endpoints. Repeat with the same seed and
verify equality. Change the seed and expect small endpoint variation, not a
different conclusion guaranteed by design.

### 4. Permute assignments

Pool outcomes and enumerate treatment-index combinations when feasible. Use a
two-sided comparison to the observed absolute difference. For large data, use
seeded Monte Carlo assignments and the plus-one p-value correction.

State why permuting individual rows is invalid if assignment occurred by
account or site.

### 5. Plan sample size

Use the Normal approximation for standardized effects 0.2, 0.5, and 0.8.
Explain why variance uncertainty, clustering, attrition, noncompliance, and a
binary metric require a more specific planner.

### 6. Control a comparison family

Complete `holm_adjust` for three p-values. Preserve original order and enforce
monotonic adjusted values after sorting. Identify the family before viewing
results; splitting an inconvenient family after analysis defeats control.

### 7. Check assignment and attrition

Compute baseline standardized difference by arm. Then remove outcomes
selectively from one arm and explain how that affects causal credibility even
if the remaining p-value is small.

### 8. Simulate peeking policy

Five ordinary looks each at alpha 0.05 are not one 0.05 decision. The lesson's
simple Bonferroni per-look split illustrates the budget. Compare it with a
single final look and research group-sequential designs before production use.

### 9. Bound the claim

Complete `claim_scope`. Randomization, intact allocation, and no severe
attrition permit a causal interpretation under additional assumptions.
Observational grouping, compromised randomization, or severe differential
attrition returns an associational scope.

## Self-check

- Fixture mean difference equals 2.
- Baseline standardized difference equals 0.
- The seeded bootstrap repeats exactly and its interval excludes zero.
- Exact permutation enumerates 12,870 assignments.
- Approximate sample size for standardized effect 0.5 is 63 per arm.
- Holm-adjusted values for 0.01, 0.04, 0.03 are 0.03, 0.06, 0.06.
- Planned looks divide or otherwise control the error budget.
- The causal claim changes when randomization or attrition assumptions fail.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_stats_01_resampling_experiments -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_stats_01_resampling_experiments -v
```

## Common pitfalls

- **Bootstrap is said to remove bias:** it quantifies uncertainty under its
  resampling assumptions; it does not repair confounding.
- **Rows are permuted despite clustered assignment:** the randomization unit was
  ignored.
- **A standardized effect hides practical units:** report both.
- **Power is computed after a nonsignificant result:** planning and
  interpretation are being confused.
- **Twenty metrics use alpha 0.05 independently:** the comparison family is
  uncontrolled.
- **The dashboard is checked daily:** an ordinary fixed-horizon p-value is
  repeatedly peeked.
- **Randomized means automatically causal:** interference, noncompliance,
  attrition, and outcome changes still matter.
- **A narrow observational interval is called causal:** precision does not
  identify an intervention effect.

## Next step

Carry the experiment plan into Python Days 35 and 45. Use `python-ml-01` to bind
the resulting data snapshot, feature schema, evaluation evidence, and promoted
artifact into a reproducible delivery record.
