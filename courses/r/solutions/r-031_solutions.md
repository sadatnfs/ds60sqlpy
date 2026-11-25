# r-031: reference reasoning

Run the [complete reference](r-031_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The missing quantity is excluded explicitly. The final row permutation preserves ID/amount alignment and makes the result deterministic.

The total is seven plus thirteen regardless of input row order. This invariant would not apply unchanged to a sequence-dependent lag calculation.

## Explained practice

### Exercise 1

Trace the two retained rows in the first example.

L1 has 8 and L3 has 9; L2 has an unknown amount.

**Approach:** Compute net for every row before filtering: L3 is 2 times 5 minus 1, L1 is 1 times 8 minus 0, and L2 has an unknown quantity.

**Why it holds here:** That gives 9, 8 and NA. The mask `!is.na(net) & net >= 8` is TRUE, TRUE, FALSE, and sorting the two survivors by id puts L1 with 8 ahead of L3 with 9.

**Tempting mistake:** Filtering with `lines[lines$net >= 8, ]`. The NA in the index produces an extra row filled with NA, so the result has three rows and one of them describes no real line.

**Verify:** `a$data$id` returns "L1" "L3", and `a$data$net` returns 8 and 9.

### Exercise 2

Raise the threshold from eight to nine.

L3 remains with net 9.

**Approach:** Call `transform_lines(lines, 9)` and keep the comparison as `>=`.

**Why it holds here:** With threshold 9, L3's net of 9 meets the boundary and L1's net of 8 falls below it. L2 is still unknown, so the mask excludes it for the same reason as before, and one row remains.

**Tempting mistake:** Switching to `>` when changing the threshold. Then `9 > 9` is FALSE, L3 is dropped too, and the result is empty, which changes the policy at the boundary instead of just the number.

**Verify:** `b$data$id` returns "L3", and `b$data$net` returns 9.

### Exercise 3

Return an exclusion count alongside the selected table.

Report input 3, retained 2, excluded 1 under the original policy.

**Approach:** Return the selected table together with `nrow(lines)`, `sum(keep)` and `sum(!keep)` from the same mask.

**Why it holds here:** keep contains no NA because of the `!is.na(net)` term, so both sums are exact counts: 2 retained, 1 excluded, 3 input. Using one mask for the table and the counts keeps them consistent.

**Tempting mistake:** Counting exclusions as `sum(lines$net < threshold, na.rm = TRUE)`. That returns 0, because L2's NA is dropped from the count, so the unknown amount disappears from the report.

**Verify:** `a$retained + a$excluded == a$input` returns TRUE, with values 2, 1 and 3.

### Exercise 4

Diagnose sorting only prices before multiplication.

Permute complete rows or join by a validated key.

**Approach:** Reorder complete rows with `lines[order(lines$id), ]`, or bring prices in through a join on a validated id, never by sorting one column.

**Why it holds here:** Sorting the prices 5, 8 and 4 into 4, 5 and 8 would give L3 a net of 2 times 4 minus 1, which is 7, and L1 a net of 5. Neither reaches 8, so the result would be empty instead of L1 and L3.

**Tempting mistake:** Calling `sort(lines$price)` before multiplying. Each column keeps its length and type, so the bug produces no error, only wrong records.

**Verify:** `transform_lines(lines[c(2, 3, 1), ])$data` returns the same ids and nets as the original call, showing that input order does not matter.

### Exercise 5

Handle an input with no qualifying rows.

Return a zero-row id/net data frame with declared types.

**Approach:** Let the same column selection run on an all FALSE mask, so the result is a zero row data frame with columns id and net.

**Why it holds here:** With threshold 100 no net qualifies. `lines[keep, c("id", "net"), drop = FALSE]` still returns both columns with their types, and ordering zero rows leaves them unchanged.

**Tempting mistake:** Returning NULL or `data.frame()` when nothing qualifies. Code that later reads `result$net` gets NULL, and binding this result to another batch fails or loses the columns.

**Verify:** `nrow(empty)` returns 0, and `names(empty)` returns "id" "net".

### Exercise 6

Transfer the pipeline to a lagged feature.

Sort by entity, time and a deterministic tie-breaker before computing lags.

**Approach:** Sort by entity, then by time, then by a deterministic tie breaker such as id, and compute each lag within its entity.

**Why it holds here:** Here ordering is part of the calculation. A lag pairs each row with the one before it, so the result depends on the row order, unlike the sum and the filter above.

**Tempting mistake:** Sorting by time only, or computing lags in arrival order. Rows from two entities interleave, so an entity's first row receives the previous entity's last value.

**Verify:** Shuffling the input rows and recomputing shows identical lag columns once both runs are sorted by entity, time and tie breaker.

## What the checks establish

The assertions confirm unique, present ids, a result ordered as L1 then L3 with nets 8 and 9, an audit of 3 input rows, 2 retained and 1 excluded, a second selection that keeps only L3 at 9, and an empty selection that still returns the `id` and `net` columns. They do not check that the exclusion rule matches a business policy you were never given.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
