# Resampling and experiments solution reasoning

Attempt `python-stats-01` before opening
[`py_stats_01_resampling_experiments_solution.py`](py_stats_01_resampling_experiments_solution.py).

The bootstrap resamples each observed arm independently and reports a
percentile interval for the difference in means. It quantifies sampling
uncertainty under an exchangeability assumption; it does not repair biased
assignment or missing outcomes. The permutation test pools outcomes under the
sharp null, enumerates all assignments when feasible, and otherwise uses a
seeded Monte Carlo estimate with a plus-one correction.

Standardized mean difference communicates effect magnitude in standard
deviation units. The Normal approximation gives a planning estimate, not a
guaranteed achieved power; final plans should reflect the actual metric,
variance, attrition, clustering, and test.

Holm adjustment controls family-wise error while being less conservative than
plain Bonferroni. Repeated unplanned peeking is another multiplicity problem;
the simple per-look alpha split illustrates planning but is not a substitute
for a designed group-sequential method.

Randomization supports causal claims only when assignment was implemented,
units did not interfere, outcome handling remained credible, and attrition did
not destroy comparability. Observational differences remain associational even
when bootstrap intervals are narrow.

Edge cases include zero variance, tiny groups, a metric chosen after seeing
results, assignment and analysis units that differ, cluster correlation,
noncompliance, missing outcomes, many secondary metrics, and stopping early
because an ordinary p-value crossed 0.05.


---

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_stats_01_resampling_experiments_solution.py`](py_stats_01_resampling_experiments_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — Define the experiment before analysis

**Prompt recap:** Write an `ExperimentPlan` containing: - assignment unit, - one primary metric and window, - minimum sample per arm, - alpha, - intended analysis, - planned stopping/looks, and - missing-outcome handling. Do this before computing outcomes.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 2 — Complete standardized effect

**Prompt recap:** Use the pooled sample standard deviation. Reject groups smaller than two and zero pooled variance. Explain raw units and standardized units side by side.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 3 — Bootstrap the difference

**Prompt recap:** Resample each arm independently with replacement, compute 2,000 differences, sort them, and select percentile endpoints. Repeat with the same seed and verify equality. Change the seed and expect small endpoint variation, not a different conclusion guaranteed by design.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 4 — Permute assignments

**Prompt recap:** Pool outcomes and enumerate treatment-index combinations when feasible. Use a two-sided comparison to the observed absolute difference. For large data, use seeded Monte Carlo assignments and the plus-one p-value correction. State why permuting individual rows is invalid if assignment occurred by account or site.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 5 — Plan sample size

**Prompt recap:** Use the Normal approximation for standardized effects 0.2, 0.5, and 0.8. Explain why variance uncertainty, clustering, attrition, noncompliance, and a binary metric require a more specific planner.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 6 — Control a comparison family

**Prompt recap:** Complete `holm_adjust` for three p-values. Preserve original order and enforce monotonic adjusted values after sorting. Identify the family before viewing results; splitting an inconvenient family after analysis defeats control.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 7 — Check assignment and attrition

**Prompt recap:** Compute baseline standardized difference by arm. Then remove outcomes selectively from one arm and explain how that affects causal credibility even if the remaining p-value is small.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 8 — Simulate peeking policy

**Prompt recap:** Five ordinary looks each at alpha 0.05 are not one 0.05 decision. The lesson's simple Bonferroni per-look split illustrates the budget. Compare it with a single final look and research group-sequential designs before production use.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 9 — Bound the claim

**Prompt recap:** Complete `claim_scope`. Randomization, intact allocation, and no severe attrition permit a causal interpretation under additional assumptions. Observational grouping, compromised randomization, or severe differential attrition returns an associational scope.

**Reference reasoning:** Resampling and tests quantify uncertainty under a design; they do not repair broken assignment, dependence, selective missingness, multiplicity, or causal assumptions. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 10 — bootstrap clustered assignments

**Prompt recap:** Extend the experiment fixture with multiple rows per account. Bootstrap accounts—not rows—within each arm and compare interval width with the incorrect row bootstrap.

**Reasoning path:** Sample independent assignment units with replacement and carry all of each selected account's observations into the resample.

Build arm-specific lists of account IDs, resample those IDs, and reconstruct
all rows belonging to each draw (including repeated accounts from replacement).
Compute the metric at the original analysis unit. The row bootstrap usually
acts as if correlated observations were independent and can understate
uncertainty.

If assignment was by site, site is the resampling unit. A small number of
clusters needs specialized methods and candid limitations.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 11 — bootstrap a ratio metric

**Prompt recap:** Estimate treatment lift for revenue per active user, preserving each user's numerator and denominator. Handle a resample with zero denominator and compare ratio-of-sums with mean-of-user-ratios.

**Reasoning path:** Define the estimand first; the two ratio formulas answer different questions. Resample complete user records.

For population revenue per active user, compute total revenue divided by total
active indicators within each resampled arm, then treatment minus/control or a
relative lift as predeclared. Reject/record a zero denominator rather than
inserting an arbitrary zero.

Mean of individual ratios weights users equally and can be undefined or answer
a different question. Report the exact formula and support with the interval.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 12 — apply covariate adjustment without leakage

**Prompt recap:** Use a pre-experiment outcome as a CUPED-style covariate. Estimate its adjustment coefficient without post-treatment information and compare unadjusted/adjusted variance and mean effect.

**Reasoning path:** The covariate must be measured before assignment and not affected by treatment. Center it with a documented analysis-sample mean.

Compute `theta = cov(outcome, premetric) / var(premetric)` using only allowed
analysis data under the predeclared method, then adjust
`outcome - theta * (premetric - mean_premetric)`. Randomization preserves the
effect estimate while a predictive covariate can reduce variance.

Check balance/missingness and report both estimates. Selecting the covariate or
formula after seeing favorable effects creates another analysis degree of
freedom.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 13 — separate intention-to-treat from treatment-on-treated

**Prompt recap:** Simulate assigned treatment with imperfect compliance. Compute the intention-to-treat effect by assignment and explain why comparing actual takers with non-takers is generally confounded.

**Reasoning path:** Random assignment protects the assignment groups, not the self-selected compliance groups.

Primary analysis groups outcomes by original randomized assignment regardless
of uptake. This estimates the policy effect of offering treatment. Actual
takers can differ in motivation, eligibility, or risk, so a naive treated
comparison loses randomization.

Instrumental-variable/complier effects require additional exclusion,
monotonicity, and relevance assumptions; state them before making that
extension.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 14 — perform missing-outcome sensitivity

**Prompt recap:** Create differential attrition by arm. Report complete-case results and bounded best/worst-case outcomes under a declared feasible outcome range.

**Reasoning path:** Missing outcomes are not automatically zero or missing completely at random. Show how strong an assumption is needed to reverse the conclusion.

Start with assignment counts and observed-outcome rates by arm. Complete-case
analysis describes observed units only. For bounded outcomes, impute favorable
and unfavorable extremes to missing rows under transparent scenarios and
recompute the effect.

The resulting range is a sensitivity analysis, not a recovered truth. Severe
differential attrition downgrades causal credibility even when observed
p-values remain small.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 15 — simulate sequential false positives

**Prompt recap:** Under a true null, simulate repeated ordinary alpha=0.05 looks and estimate ever-reject probability. Compare one final look, the lesson's simple alpha split, and a clearly labeled exploratory monitor.

**Reasoning path:** Use a seeded outer simulation and record the first crossing. The simple split illustrates budgeting; it is not an optimized group-sequential design.

Generate null outcomes according to the planned arrival process, evaluate each
look using only data available then, and estimate the fraction of simulations
that ever cross. Multiple unadjusted opportunities exceed the nominal one-look
error. Dividing alpha across planned looks is conservative but demonstrates
control.

Do not tune the simulation until a preferred policy wins. Production use
requires a reviewed sequential design and operational stopping rules.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 16 — pre-specify heterogeneous effects

**Prompt recap:** Choose two domain-motivated subgroups before analysis, estimate effects with uncertainty and support, and adjust the planned comparison family. Contrast this with mining many cuts for the largest lift.

**Reasoning path:** An interaction test addresses whether effects differ; significance in one subgroup and not another is not itself evidence of difference.

Record subgroup definitions and multiplicity family in the ExperimentPlan.
Report each arm's sample size and effect interval plus a direct interaction or
difference-in-effects estimate. Sparse groups receive cautious or no claim.

Data-mined segments are hypothesis generation and need independent
confirmation. Avoid causal stories for a subgroup selected because its
observed lift was largest.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 17 — run clustered randomization inference

**Prompt recap:** For a site-randomized experiment, permute site assignments while keeping all rows within a site together. Compare with invalid row-level permutation and state the sharp-null interpretation.

**Reasoning path:** Enumerate or sample assignments consistent with the original design, including treated-site count and any stratification.

Compute the observed statistic from site assignments. Generate only legal
site-level reallocations, reconstruct row outcomes under each assignment, and
use the plus-one Monte Carlo correction when sampling. The p-value describes
extremeness under the sharp null and assignment mechanism.

Row permutation fabricates assignments that could never occur and overstates
independent information. Few sites limit resolution and power.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 18 — produce an auditable analysis packet

**Prompt recap:** Write a deterministic JSON/Markdown packet containing plan hash, data fingerprint, exclusions, assignment checks, attrition, estimand, effect, interval, adjusted p-values, claim scope, code version, and limitations.

**Reasoning path:** Generate machine-readable values and prose from one result object. Keep random seeds and units visible; exclude raw sensitive rows.

Canonicalize the plan and dataset identity before analysis, then serialize
finite numeric results with explicit metric units and denominators. The report
links every claim to its design/evidence and labels exploratory analyses.
Rerunning with identical inputs and seed should reproduce the packet.

Hashes identify bytes but do not prove legal use or study quality. Preserve
review ownership and any deviations from the pre-analysis plan.

**Common trap:** Resampling individual rows, choosing metrics/stopping after results, or reporting a narrow interval as causal certainty can produce precise but invalid conclusions.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.
