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

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_stats_01_resampling_experiments.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_stats_01_resampling_experiments.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

Resampling approximates repeated sampling under an explicit scheme. A
bootstrap samples observational units with replacement to estimate an
estimator's sampling variability. A permutation test shuffles labels
under an exchangeability/null assumption to build a reference
distribution. Clustered or temporal data needs cluster/block schemes.

In an experiment, the estimand states the effect being targeted, such
as difference in means under assigned treatment. Random assignment
supports causal interpretation when assignment, interference,
attrition, compliance, and measurement assumptions are credible.
Observational adjustment does not recreate randomization automatically.

- **resampling unit:** matches the independent assignment/observation grain rather than blindly sampling rows.
- **seeded bootstrap/permutation loop:** produces a reproducible distribution of a declared statistic with Monte Carlo error.
- **estimand + assignment mechanism:** defines which causal contrast is identified and which assumptions support it.

### Micro-example A — bootstrap a mean difference with a seeded generator

```python
import numpy as np

control = np.array([2.0, 2.5, 3.0, 3.5, 4.0])
treatment = np.array([3.0, 3.5, 4.0, 4.5, 5.0])
rng = np.random.default_rng(6101)
draws = np.empty(5_000)
for index in range(draws.size):
    c = rng.choice(control, size=control.size, replace=True)
    t = rng.choice(treatment, size=treatment.size, replace=True)
    draws[index] = t.mean() - c.mean()
interval = np.quantile(draws, [0.025, 0.975])
print({"estimate": treatment.mean() - control.mean(), "interval": interval})
```

**Expected observation:** The resampled interval describes uncertainty under independent within-group resampling; the small sample makes it wide/discrete.

**Why it matters:** Rows are independent units and each group's empirical distribution is a useful population proxy.

### Micro-example B — build a randomization-style null distribution

```python
import numpy as np

outcomes = np.array([1, 2, 3, 4, 7, 8, 9, 10], dtype=float)
assigned = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=int)
observed = outcomes[assigned == 1].mean() - outcomes[assigned == 0].mean()
rng = np.random.default_rng(6102)
null = []
for _ in range(5_000):
    shuffled = rng.permutation(assigned)
    null.append(
        outcomes[shuffled == 1].mean() - outcomes[shuffled == 0].mean()
    )
p_value = np.mean(np.abs(null) >= abs(observed))
print({"observed": observed, "two_sided_p": p_value})
```

**Expected observation:** The null distribution comes from assignments consistent with the shuffle rule, not from a parametric t formula.

**Why it matters:** Treatment labels are exchangeable under the sharp null and the design had no cluster/strata restrictions.

### Debugging and transfer

**Common mistake:** Resampling rows independently when treatment or outcomes are clustered, repeated, or time-dependent.

**Diagnostic:** Write the estimand, unit, assignment/sampling mechanism, statistic, resampling rule, seed/runs, interval/test convention, and assumption violations.

**Transfer question:** How would both examples change if four observations came from two households rather than eight independent people?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

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

**Verify:** For task `Define the experiment before analysis`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then run the named missing/unknown/empty boundary and assert its explicit fallback or exception instead of accepting an accidental default.







### 2. Complete standardized effect

Use the pooled sample standard deviation. Reject groups smaller than two and
zero pooled variance. Explain raw units and standardized units side by side.

**Verify:** For task `Complete standardized effect`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.







### 3. Bootstrap the difference

Resample each arm independently with replacement, compute 2,000 differences,
sort them, and select percentile endpoints. Repeat with the same seed and
verify equality. Change the seed and expect small endpoint variation, not a
different conclusion guaranteed by design.

**Verify:** For task `Bootstrap the difference`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### 4. Permute assignments

Pool outcomes and enumerate treatment-index combinations when feasible. Use a
two-sided comparison to the observed absolute difference. For large data, use
seeded Monte Carlo assignments and the plus-one p-value correction.

State why permuting individual rows is invalid if assignment occurred by
account or site.

**Verify:** For task `Permute assignments`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### 5. Plan sample size

Use the Normal approximation for standardized effects 0.2, 0.5, and 0.8.
Explain why variance uncertainty, clustering, attrition, noncompliance, and a
binary metric require a more specific planner.

**Verify:** For task `Plan sample size`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### 6. Control a comparison family

Complete `holm_adjust` for three p-values. Preserve original order and enforce
monotonic adjusted values after sorting. Identify the family before viewing
results; splitting an inconvenient family after analysis defeats control.

**Verify:** For task `Control a comparison family`, show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.







### 7. Check assignment and attrition

Compute baseline standardized difference by arm. Then remove outcomes
selectively from one arm and explain how that affects causal credibility even
if the remaining p-value is small.

**Verify:** For task `Check assignment and attrition`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then show the formula or intermediate quantities and check the final value independently rather than trusting one library call.







### 8. Simulate peeking policy

Five ordinary looks each at alpha 0.05 are not one 0.05 decision. The lesson's
simple Bonferroni per-look split illustrates the budget. Compare it with a
single final look and research group-sequential designs before production use.

**Verify:** For task `Simulate peeking policy`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### 9. Bound the claim

Complete `claim_scope`. Randomization, intact allocation, and no severe
attrition permit a causal interpretation under additional assumptions.
Observational grouping, compromised randomization, or severe differential
attrition returns an associational scope.

**Verify:** For task `Bound the claim`, show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.







### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 10 — bootstrap clustered assignments

Extend the experiment fixture with multiple rows per account. Bootstrap accounts—not rows—within each arm and compare interval width with the incorrect row bootstrap.

**Progressive hint:** Sample independent assignment units with replacement and carry all of each selected account's observations into the resample.

**Verify:** For task `bootstrap clustered assignments`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 11 — bootstrap a ratio metric

Estimate treatment lift for revenue per active user, preserving each user's numerator and denominator. Handle a resample with zero denominator and compare ratio-of-sums with mean-of-user-ratios.

**Progressive hint:** Define the estimand first; the two ratio formulas answer different questions. Resample complete user records.

**Verify:** For task `bootstrap a ratio metric`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 12 — apply covariate adjustment without leakage

Use a pre-experiment outcome as a CUPED-style covariate. Estimate its adjustment coefficient without post-treatment information and compare unadjusted/adjusted variance and mean effect.

**Progressive hint:** The covariate must be measured before assignment and not affected by treatment. Center it with a documented analysis-sample mean.

**Verify:** For task `apply covariate adjustment without leakage`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 13 — separate intention-to-treat from treatment-on-treated

Simulate assigned treatment with imperfect compliance. Compute the intention-to-treat effect by assignment and explain why comparing actual takers with non-takers is generally confounded.

**Progressive hint:** Random assignment protects the assignment groups, not the self-selected compliance groups.

**Verify:** For task `separate intention-to-treat from treatment-on-treated`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 14 — perform missing-outcome sensitivity

Create differential attrition by arm. Report complete-case results and bounded best/worst-case outcomes under a declared feasible outcome range.

**Progressive hint:** Missing outcomes are not automatically zero or missing completely at random. Show how strong an assumption is needed to reverse the conclusion.

**Verify:** For task `perform missing-outcome sensitivity`, run the named missing/unknown/empty boundary and assert its explicit fallback or exception instead of accepting an accidental default.







### Exercise 15 — simulate sequential false positives

Under a true null, simulate repeated ordinary alpha=0.05 looks and estimate ever-reject probability. Compare one final look, the lesson's simple alpha split, and a clearly labeled exploratory monitor.

**Progressive hint:** Use a seeded outer simulation and record the first crossing. The simple split illustrates budgeting; it is not an optimized group-sequential design.

**Verify:** For task `simulate sequential false positives`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 16 — pre-specify heterogeneous effects

Choose two domain-motivated subgroups before analysis, estimate effects with uncertainty and support, and adjust the planned comparison family. Contrast this with mining many cuts for the largest lift.

**Progressive hint:** An interaction test addresses whether effects differ; significance in one subgroup and not another is not itself evidence of difference.

**Verify:** For task `pre-specify heterogeneous effects`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then show the formula or intermediate quantities and check the final value independently rather than trusting one library call.







### Exercise 17 — run clustered randomization inference

For a site-randomized experiment, permute site assignments while keeping all rows within a site together. Compare with invalid row-level permutation and state the sharp-null interpretation.

**Progressive hint:** Enumerate or sample assignments consistent with the original design, including treated-site count and any stratification.

**Verify:** For task `run clustered randomization inference`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 18 — produce an auditable analysis packet

Write a deterministic JSON/Markdown packet containing plan hash, data fingerprint, exclusions, assignment checks, attrition, estimand, effect, interval, adjusted p-values, claim scope, code version, and limitations.

**Progressive hint:** Generate machine-readable values and prose from one result object. Keep random seeds and units visible; exclude raw sensitive rows.

**Verify:** For task `produce an auditable analysis packet`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then verify identity/hash and metadata, then reload or inspect the artifact outside the creating state and test one tampered mismatch.







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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-stats-01` — Resampling, experiments, and causal boundaries.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize bootstrap and permutation resampling, experimental estimands, and causal boundaries. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_stats_01_resampling_experiments.md`
- learner artifact: `python/professional/lessons/py_stats_01_resampling_experiments.py`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
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
