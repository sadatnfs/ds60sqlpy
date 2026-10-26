# dax-041: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-041_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A comparable full-month category

FullJanuary 2025 and Paper category; Budget is monthly/category-grained and disconnected.

| Actual | ComparableBudget | Variance |
| --- | --- | --- |
| 47 | 60 | -13 |

The sign convention is part of the metric: here negative means below the revenue target, not necessarily a generic unfavorable variance for every account type.

- January has 31 selected dates, satisfying the complete single-month guard.
- Paper actuals are S 4 and S 5:27 +20 =47.
- The mapped budget is 60, so actual minus budget is-13.

### Case B: A daily selection is not assigned the monthly target

One observed day in January 2025; no daily budget allocation policy exists.

| Actual | ComparableBudget |
| --- | --- |
| 27 | BLANK |

BLANK protects an undefined comparison. If a daily target is required, add and explain an allocation policy rather than removing the guard without replacement.

- The selected date count is 1 rather than January's31.
- Actual revenue on the day is 27.
- The guard refuses to present the whole-month 60 as a comparable daily budget.

## Explained practice answers

### Exercise 1

Predict February Home actual and budget.

Actual 36, budget 50 and variance-14.

### Exercise 2

Combine both January categories.

Actual 67, budget 90 and variance-23.

### Exercise 3

Specify a uniform daily allocation for January Paper.

Each of 31 calendar days receives 60/31; the complete-month allocation reconciles to 60. This is a chosen policy, not an observed daily target.

### Exercise 4

Diagnose attaching 60 to every January sales line then summing.

The result depends on transaction count and overstates the budget. Aggregate or allocate at a compatible grain.

### Exercise 5

Explain a missing category-budget row.

Keep an unavailable-budget signal or a declared exclusion; do not invent a variance by silently coalescing the target to zero.

### Exercise 6

Transfer the rule to headcount plans and employee events.

Define comparable populations and allocation before joining or summing them, and reconcile the allocated total to the plan.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
