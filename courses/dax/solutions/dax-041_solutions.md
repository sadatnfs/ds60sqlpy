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
- Paper actuals are S4 and S5: 27 + 20 = 47.
- The mapped budget is 60, so actual minus budget is -13.

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

Actual 36, budget 50 and variance -14.

**Why it fits this model:** February Home has one sale, S8 at 36, and one monthly budget row, 202502 Home 50. The full-month guard holds, so variance is 36 - 50.

**Tempting mistake:** Leaving out the Category TREATAS assigns the whole February budget, 25 + 50 = 75, to Home.

**How to confirm:** With MonthNumber 2 and Category Home, expect Actual 36, ComparableBudget 50 and Variance -14.

### Exercise 2

Combine both January categories.

Actual 67, budget 90 and variance -23.

**Why it fits this model:** Without a category filter, VALUES(Product[Category]) returns every category, so TREATAS picks both January budget rows, 60 + 30. Actuals are 47 + 20.

**Tempting mistake:** Averaging the category attainment ratios, 47 / 60 (0.783) and 20 / 30 (0.667), gives 0.725 instead of the combined 67 / 90, about 0.744.

**How to confirm:** For full January 2025 without a category filter, expect Actual 67, ComparableBudget 90 and Variance -23.

### Exercise 3

Specify a uniform daily allocation for January Paper.

Each of 31 calendar days receives 60/31; the complete-month allocation reconciles to 60. This is a chosen policy, not an observed daily target.

**Why it fits this model:** A uniform policy gives each of January's 31 days 60 / 31, about 1.94, and the days add back to 60.

**Tempting mistake:** Dividing by the 2 days with Paper sales (January 2 and 3) puts 30 on each, so the target depends on when sales happened.

**How to confirm:** January 2 gets about 1.94 against an actual of 27; the 31 daily allocations sum to 60.

### Exercise 4

Diagnose attaching 60 to every January sales line then summing.

The result depends on transaction count and overstates the budget. Aggregate or allocate at a compatible grain.

**Why it fits this model:** Budget is monthly by category. January Paper has two lines, S4 and S5, so attaching the target to each line repeats it.

**Tempting mistake:** Using `SUMX ( Sales, 60 )` for January Paper gives 120, double the target, and would grow with every extra line.

**How to confirm:** The compatible-grain target is 60; compare it with an actual of 47.

### Exercise 5

Explain a missing category-budget row.

Keep an unavailable-budget signal or a declared exclusion; do not invent a variance by silently coalescing the target to zero.

**Why it fits this model:** Travel has no budget row, and if 202502 Home were missing, February Home would have no target either.

**Tempting mistake:** Coalescing a missing target to 0 turns February Home into a variance of +36 when it has no target.

**How to confirm:** With the row removed, ComparableBudget should be BLANK and the measure should flag a missing budget rather than return 36.

### Exercise 6

Transfer the rule to headcount plans and employee events.

Define comparable populations and allocation before joining or summing them, and reconcile the allocated total to the plan.

**Why it fits this model:** Headcount plans are often by department and quarter, while hires and exits are individual events with dates. Like Budget against Sales, compare them at the plan's grain.

**Tempting mistake:** Joining the quarterly plan to each hire event and summing repeats the plan per hire, just as 60 per sales line did.

**How to confirm:** Aggregate events to department and quarter, compare with the plan, and if allocating to months, check that the months add back to the plan.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
