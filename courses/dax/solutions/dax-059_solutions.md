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

**Why it fits this model:** Assignments define the denominator. Exposure events can repeat, so a new U3 event adds an event and nothing else.

**Tempting mistake:** Using COUNTROWS(Exposures) as the denominator. With 3 events, Treatment's rate would become 2 / 3 instead of 1.

**How to confirm:** Treatment shows Assigned 2, Converted 2, ExposedUnits 1, ExposureEvents 3 and AssignedUnitRate 1.

### Exercise 2

Remove U4 merely because no exposure is recorded.

Do not silently remove it from an intention-to-treat denominator. Any alternative exposure-based analysis needs its own justified design and labeling.

**Why it fits this model:** The intention-to-treat estimand counts every assigned unit. U4 was assigned to Treatment and converted, whether or not an exposure was recorded.

**Tempting mistake:** Dropping U4 because it has no exposure. Treatment's rate stays 1 (1 / 1), which hides that the denominator went from 2 to 1.

**How to confirm:** Keep Treatment at 2 assigned and 2 converted; label any exposure-based analysis separately with its own design.

### Exercise 3

Write the quality matrix needed before interpreting the arm contrast.

Check one assignment per unit, stable arm membership, outcome coverage, duplicate exposures, timing, eligibility and the provenance of any supplied uncertainty summary.

**Why it fits this model:** Before reading Treatment 1 and Control 0.5, check that each unit has one assignment, one outcome and clean events.

**Tempting mistake:** Checking only the rate column. That misses that U3 has two exposure events and U4 has none.

**How to confirm:** COUNTROWS(Assignments) = DISTINCTCOUNT(Assignments[UnitID]) = 4, 4 outcome rows, exposure events per unit (U3 has 2), and the provenance of the Wilson summary.

### Exercise 4

Diagnose claiming statistical certainty because Treatment's observed rate is 1.

The supplied Wilson lower bound is about 0.3424; the population rate is not known to equal 1, and study validity needs additional evidence.

**Why it fits this model:** With n = 2, an observed rate of 1 is consistent with much lower true rates.

**Tempting mistake:** Reporting "100 percent conversion" as certain. The supplied interval says otherwise.

**How to confirm:** Report Treatment as 1 with a Wilson interval of about 0.342 to 1, and Control as 0.5 with about 0.095 to 0.905.

### Exercise 5

Explain why comparing arm interval overlap is not a complete treatment-effect test.

Use an appropriate difference/ratio analysis with assumptions and multiplicity/sequential considerations; marginal intervals are not a substitute.

**Why it fits this model:** The question is about the difference between arms, which has its own sampling distribution.

**Tempting mistake:** Reading the overlap of 0.095 to 0.905 and 0.342 to 1 as "no effect", or a lack of overlap as significance.

**How to confirm:** Compute an interval for the 0.5 difference with a stated method; with two units per arm it will be wide.

### Exercise 6

Connect this report to the cohort model.

Report cohort age/coverage, retain eligible units and separate unobserved follow-up from failures before comparing groups.

**Why it fits this model:** Cohorts need the same care: members come from CohortMember, and follow-up depends on how long the cohort has been observed.

**Tempting mistake:** Scoring the 202502 cohort's month-one retention as 0 of 2. March 2025 is after the February 28 observation end.

**How to confirm:** Month zero: 202501 is 2 of 2 (A1, A3) and 202502 is 1 of 2 (A4). Month one: 202501 is 1 of 2 (A2), and 202502 is unobserved.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
