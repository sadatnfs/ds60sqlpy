# dax-040: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-040_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: January cohort at one-month age

Analytics cohort population; January entrants 100/200; activity observed through February 2025.

| EligibleMembers | ActiveAtEntry | ActiveAtAgeOne | RetentionAtAgeOne |
| --- | --- | --- | --- |
| 2 | 2 | 1 | 0.5 |

This denominator is the entry cohort, not the subset observed active in a later month. Filtering to active members before counting eligibility would inflate retention.

- Both January members remain in the eligible denominator.
- Both are active in January, but only 100 is active in February.
- One-month retention is 1/2, regardless of how many events member 100 generated.

### Case B: A newer cohort has unavailable follow-up

February entrants 300/400; March follow-up is outside the declared observed months.

| EligibleMembers | ActiveAtEntry | EntryActivityRate | RetentionAtAgeOne |
| --- | --- | --- | --- |
| 2 | 1 | 0.5 | BLANK |

The two 50-percent values in the lesson have different ages and meanings. A matrix must expose both cohort month and observation age.

- Both members are enrolled, but only 300 has February activity.
- Entry activity is 1/2.
- Month-one retention asks about March, so the coverage guard returns BLANK rather than an invented zero.

## Explained practice answers

### Exercise 1

Predict January retention if member 100 has three February events.

Retention stays 1/2. An event-count numerator would incorrectly inflate it.

### Exercise 2

Add a February event for member 200.

Both January members would be active at age one, so retention becomes 1.

### Exercise 3

Write a cohort metric contract.

For this fixture: enrolled members by signup month, any observed activity in the target calendar month, distinct member count, full enrollment denominator and a coverage guard.

### Exercise 4

Diagnose dropping inactive member 400 before calculating the February entry rate.

It would turn 1/2 into 1/1 and conceal inactive eligible members.

### Exercise 5

Explain why 202512 +1 is not a valid next-month calculation.

It gives 202513. Use a date-aware calendar mapping or EDATE with explicit period membership.

### Exercise 6

Transfer the coverage rule to survival follow-up.

Retain observation time and censoring status; choose an estimator matching those assumptions rather than zero-filling future outcomes.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
