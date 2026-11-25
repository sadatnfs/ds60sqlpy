# Diagnose allocation and measurement integrity

Tutorial ID: `statistics-exp-005`. Prerequisites: `statistics-exp-003`, `statistics-009`. Complete example: [experiment_05.py](examples/experiment_05.py).

## Key terms

- **Sample ratio mismatch:** Disagreement between observed arm counts and the counts the assignment probabilities imply; it signals incompatibility with the assignment model but does not identify the cause.
- **Pearson statistic:** The sum over arms of squared differences between observed and expected counts divided by the expected counts, approximately chi-square with one degree of freedom for two arms.
- **A/A test:** An experiment in which both arms receive the same experience, used to check that alarms and tests fire at their nominal rate.
- **Monte Carlo standard error:** The simulation uncertainty in an estimated alarm or rejection rate, which shrinks as the number of simulated replicates grows.

## A count discrepancy is a symptom

Sample ratio mismatch asks whether observed allocation counts agree with the assignment model. Under independent 50/50 assignment, the expected counts in two arms are \(n/2\). Pearson's statistic is

\[
X^2=\sum_{a\in\{0,1\}}\frac{(O_a-E_a)^2}{E_a}.
\]

Its large-count reference is approximately chi-square with one degree of freedom. A small p-value signals incompatibility with the model. It cannot identify whether the cause is assignment, execution, event delivery or an analyst's filtering rule.

Our shared fixture deliberately uses complete randomization with exactly 120 users per arm. Those counts are fixed by construction, so a multinomial SRM model is not its literal randomization distribution. The example reports its trivial balanced count diagnostic, then uses independent binomial allocation for the A/A simulation, where that reference is appropriate. This distinction matters: use the randomization mechanism actually implemented.

## Work a localized failure

Delete all treatment/mobile users from a downstream stage. The overall allocation comparison now has p about .0075. Device-specific counts show 42 control mobile users and zero treatment mobile users. That pattern directs investigation toward the treatment/mobile path, while the unchanged assignment log shows the loss occurred after assignment.

This is stronger evidence than a single dashboard color because the stage and subgroup comparison has an identifiable mechanism. In a real pipeline, inspect software version, logging schema, trigger rules and event latency. Treat the subgroup search as diagnosis, not as a collection of unadjusted confirmatory treatment-effect tests.

## Work an A/A calibration experiment

The second case simulates 4,000 independent allocations of 1,000 users under a true 50/50 mechanism. At a diagnostic alpha of .01, the observed alarm rate is about .00925. The Monte Carlo SE near .01 is about .00157. The code checks closeness using a tolerance tied to this uncertainty rather than demanding exactly 1% alarms.

A/A outcome tests should separately exercise metric calculation, dependence handling and stopping rules. Correct allocation calibration alone does not test outcome inference. A shared measurement bias can affect both arms equally and pass A/A, yet fail when a treatment changes the measurement pathway. Unit 08 tests monitoring behavior, and unit 03 shows treatment-dependent missingness.

## Make investigation reproducible

Record the assignment probabilities, the counted population, the observation timestamp and the exact exclusion rules. A partially ingested day's data can have unequal delays without permanent missingness. Waiting for defined maturity is different from deleting late events. Repeatedly testing the same count stream also changes the alarm procedure; calibrate repeated integrity monitoring or treat an alert as a conservative diagnostic with an explicit investigation policy.

**Answered discussion: Does balance prove randomization?** No. Deterministic alternation can give perfectly equal counts while aligning assignment with time. A faulty identifier hash can be balanced overall but correlate with device or geography. Verify the assignment mechanism and identity persistence, not just the realized counts.

## Worked example: how much loss can SRM see?

Compute Pearson's statistic by hand for a treatment arm that loses a growing number of its 120 users at some downstream stage. Run it in [experiment_05.py](examples/experiment_05.py), where `stats` is already imported.

```python prelude=examples/experiment_05.py
for lost in [0, 5, 10, 20, 38]:
    counts = np.array([120, 120 - lost])
    expected = counts.sum() / 2
    x2 = ((counts - expected) ** 2 / expected).sum()
    print(f"lost {lost:2d}: X2={x2:6.3f} p={stats.chi2.sf(x2, 1):.4f}")
```

```text
lost  0: X2= 0.000 p=1.0000
lost  5: X2= 0.106 p=0.7443
lost 10: X2= 0.435 p=0.5097
lost 20: X2= 1.818 p=0.1775
lost 38: X2= 7.149 p=0.0075
```

The last row reproduces the localized-failure case: losing all 38 treated mobile users gives p about .0075. The earlier rows are the uncomfortable part. Losing 20 treated users, one sixth of the arm, yields p about .18, which no reasonable alarm threshold flags, yet unit 03 showed that losing 25 selected users can distort conversion substantially. SRM power grows with the total count, so a large production experiment detects small proportional losses that this 240-user fixture cannot. A quiet SRM check on a small experiment is weak evidence of integrity; stage-by-stage reconciliation is the stronger control.

## Worked example: balanced counts from a broken assignment rule

A faulty rule can produce exactly equal arms. Here a hash bug assigns treatment whenever `unit % 6` is 0, 1 or 3.

```python
users, _, _, _ = experiment_fixture()
faulty = users.unit.mod(6).isin([0, 1, 3]).astype(int)
print("arm counts:", faulty.value_counts().sort_index().tolist())
print("SRM p:", stats.chisquare(faulty.value_counts()).pvalue)
print(pd.crosstab(users.device, faulty))
```

```text
arm counts: [120, 120]
SRM p: 1.0
unit       0   1
device
desktop  120  40
mobile     0  80
```

Allocation is a perfect 120 to 120, so SRM reports p equal to one. The crosstab shows that every mobile user landed in treatment, because the fixture defines mobile as `unit % 3 == 0`, and residues 0 and 3 modulo 6 are both in the faulty set. Any device difference in outcomes would now be indistinguishable from the treatment effect. The diagnostic that catches this is a covariate balance check on pretreatment attributes, here a crosstab, interpreted alongside the assignment code.

## What a passing integrity check licenses

A passing SRM and A/A calibration license only the narrow claims they test: counts match the allocation model, and the allocation reference behaves as expected under the null. They do not show that outcomes are measured identically across arms or that identity is stable across devices. Record which checks ran, at which stage, and what defect each could have detected.

Continue to [fixed-horizon inference](06-fixed-horizon-analysis.md). Primary reference: [SRM taxonomy and diagnosis](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/).
