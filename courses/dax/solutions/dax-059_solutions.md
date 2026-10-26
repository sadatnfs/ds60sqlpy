# dax-059: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-059_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Assignment and exposure integrity

Analytics experiment fixture; all four assigned units have one complete outcome; exposure is a separate repeated-event stream.

| Arm | Assigned | Converted | ExposedUnits | ExposureEvents | AssignedUnitRate |
| --- | --- | --- | --- | --- | --- |
| Control | 2 | 1 | 2 | 2 | 0.5 |
| Treatment | 2 | 2 | 1 | 2 | 1 |

The observed difference 0.5 is a descriptive contrast in this synthetic fixture, not evidence that the assignment or measurement process supports causal inference.

- Control U1/U2 yield one conversion among two assignments.
- Treatment U3/U4 yield two conversions, but both treatment exposure events belong to U3.
- Assigned-unit rates are 0.5 and 1; exposure counts reveal a separate coverage/duplication issue.

### Case B: Display supplied uncertainty without overstating it

Supplied marginal 95 percent Wilson score intervals for each arm's binomial rate; n=2 per arm; not a difference interval.

| Arm | Rate | WilsonLower | WilsonUpper |
| --- | --- | --- | --- |
| Control | 0.5 | 0.09453120573 | 0.9054687943 |
| Treatment | 1 | 0.3423802275 | 1 |

The interval table has its own method and assumptions. Displaying it accurately is different from validating the scientific design or calculating a treatment-effect confidence interval.

- Control has k=1,n=2 and estimate 0.5.
- Treatment has k=2,n=2 and estimate 1.
- The marginal intervals remain wide; an all-successes sample does not imply a known population rate of 1.

## Explained practice answers

### Exercise 1

Predict the treatment exposure-event count after another U3 event.

Events become 3, distinct exposed units stay 1, assignments stay 2 and the assigned-unit conversion rate stays 1.

### Exercise 2

Remove U4 merely because no exposure is recorded.

Do not silently remove it from an intention-to-treat denominator. Any alternative exposure-based analysis needs its own justified design and labeling.

### Exercise 3

Write the quality matrix needed before interpreting the arm contrast.

Check one assignment per unit, stable arm membership, outcome coverage, duplicate exposures, timing, eligibility and the provenance of any supplied uncertainty summary.

### Exercise 4

Diagnose claiming statistical certainty because Treatment's observed rate is 1.

The supplied Wilson lower bound is about 0.3424; the population rate is not known to equal 1, and study validity needs additional evidence.

### Exercise 5

Explain why comparing arm interval overlap is not a complete treatment-effect test.

Use an appropriate difference/ratio analysis with assumptions and multiplicity/sequential considerations; marginal intervals are not a substitute.

### Exercise 6

Connect this report to the cohort model.

Report cohort age/coverage, retain eligible units and separate unobserved follow-up from failures before comparing groups.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
