# Diagnose allocation and measurement integrity

Tutorial ID: `statistics-exp-005`. Prerequisites: `statistics-exp-003`, `statistics-009`. Complete example: [experiment_05.py](examples/experiment_05.py).

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

Continue to [fixed-horizon inference](06-fixed-horizon-analysis.md). Primary reference: [SRM taxonomy and diagnosis](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/).
