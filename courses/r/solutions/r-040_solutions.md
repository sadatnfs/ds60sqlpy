# r-040: reference reasoning

Use the [complete reference](r-040_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The unknown measurement is excluded under a finite-nonnegative policy, while every admitted segment has exactly one dimension match.

Alpha has one admitted record and Beta has two. The final observation mean uses all three rather than equal weighting of the two group means.

## Explained practice

### Exercise 1

Derive the overall admitted mean.

It is 70/3.

**Approach:** Divide the admitted total by the admitted count once: 70 over 3.

**Why it holds here:** The admitted amounts are 10, 20 and 40; R3 is rejected because its amount is NA. So the total is 70, the count is 3, and the mean is 70/3, about 23.33.

**Tempting mistake:** Averaging the group means 10 and 30 to get 20, which weights Alpha's single record like Beta's two. Counting R3 as 0 gives 70/4 = 17.5, which is also wrong.

**Verify:** `isTRUE(all.equal(result$overall, 70 / 3))` returns TRUE.

### Exercise 2

Change R3 to a valid amount 30.

Count becomes 4, total 100 and overall mean 25.

**Approach:** Set R3's amount to 30 and rerun the whole pipeline.

**Why it holds here:** R3 now passes `is.finite` and the nonnegative rule, so 4 records are admitted with total 100 and the overall mean is 25. Alpha's row becomes count 2, total 40 and mean 20.

**Tempting mistake:** Updating the stored total to 100 by hand while keeping the count at 3, which gives 33.33.

**Verify:** `analyze(changed, dimension)$overall == 25` returns TRUE.

### Exercise 3

Assemble validate, enrich, summarize into one callable pipeline.

The stages preserve unique IDs and reconcile admitted/group totals.

**Approach:** Put validation, enrichment and summary in one function that returns the report together with the input, admitted, rejected and overall fields.

**Why it holds here:** The stages check each other: the type and uniqueness checks run first, `!anyNA(index)` confirms every admitted segment has a label, and the reconciliation confirms the report counts add to 3 and its totals to 70.

**Tempting mistake:** Returning only the report. A reader would see 3 records described and could not tell that a fourth was rejected for a missing amount.

**Verify:** `result$input`, `result$admitted` and `result$rejected` return 4, 3 and 1.

### Exercise 4

Diagnose a duplicated segment dimension.

Reject it before any join can multiply records.

**Approach:** Check `anyDuplicated(dimension$segment)` before matching and stop if it is not 0.

**Why it holds here:** `rbind(dimension, dimension[1, ])` adds a second A row. With the check, analyze stops before any join; without it, a merge would pair R1 with both A rows and give 4 rows totaling 80.

**Tempting mistake:** Removing duplicate rows with unique() and continuing. That works here only because both A rows say Alpha; when two rows give different labels, unique keeps both.

**Verify:** `bad` returns TRUE, which shows analyze raised an error for the duplicated dimension.

### Exercise 5

Handle a batch with no admitted records.

Return an empty group report, count 0 and an explicit missing mean.

**Approach:** Return an empty report that keeps all four columns, an admitted count of 0 and an overall mean of NA_real_.

**Why it holds here:** With every amount NA, all 4 records are rejected and no group exists. A mean of nothing is undefined, so NA is the honest value, and the fixed columns let downstream code read the report without special cases.

**Tempting mistake:** Computing `sum(data$amount) / nrow(data)` regardless. It returns 0/0, which is NaN, and a report with no columns breaks any code that selects count or total.

**Verify:** `is.na(empty_result$overall)` returns TRUE, and `names(empty_result$report)` returns label, count, total and mean.

### Exercise 6

Write a bounded analyst handoff.

State source, grain, admission, join policy, metric definitions, actual checks and limits on generalization.

**Approach:** Write the handoff from the result fields: source and grain, the admission rule, the join policy, the metric definitions, the checks that ran and the limits.

**Why it holds here:** Each claim maps to a field: 4 records with one row per id, 1 rejected for a missing amount, a many to one join on a unique segment key, and Alpha with 1 record against Beta with 2.

**Tempting mistake:** Writing that Beta customers spend three times as much as Alpha. That rests on 1 and 2 records, and the missing amount may not be missing at random.

**Verify:** Every number in the handoff matches a value that result shows: the two report rows, input 4, admitted 3, rejected 1 and overall about 23.33.

## What the checks establish

The reference makes 12 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
