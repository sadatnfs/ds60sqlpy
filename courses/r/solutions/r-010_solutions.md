# r-010: reference reasoning

Run the [complete reference](r-010_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The row permutation is applied to the entire data frame. Each ID retains its original amount.

The complete mask excludes the unknown amount. drop=FALSE preserves a table even though only one row and one column remain.

## Explained practice

### Exercise 1

Count rows and columns in a three-record two-field table.

nrow is three and ncol is two.

**Approach:** Call `nrow(records)` and `ncol(records)`, or `dim(records)` for both at once.

**Why it holds here:** The starter holds three ids, B, A and C, each with one amount, so the table is three records by two fields.

**Tempting mistake:** Using `length(records)`. A data frame is a list of columns, so length returns 2, the column count, and a reader expecting a row or cell count gets the wrong number.

**Verify:** `dim(records)` returns c(3L, 2L) before the fee column is added.

### Exercise 2

Add a derived amount_with_fee column.

Each row retains its ID and gains amount plus the declared fee.

**Approach:** Assign `records$amount_with_fee <- records$amount + 2` on the unsorted table.

**Why it holds here:** The addition is vectorized over aligned positions, so each row adds the fee to its own amount: B 22, A 12, C 32.

**Tempting mistake:** Computing the fee from a sorted copy, such as `sort(records$amount) + 2`, and assigning it back. B would get 12, which is A's amount plus the fee.

**Verify:** The reference check `identical(records$amount_with_fee, c(22, 12, 32))` returns TRUE, and the B row shows 22.

### Exercise 3

Validate a nonmissing unique ID column.

Use !anyNA(id) and !anyDuplicated(id).

**Approach:** Require both `!anyNA(records$id)` and `!anyDuplicated(records$id)`.

**Why it holds here:** B, A and C are all present and distinct, so both conditions hold. Missing and repeated keys are separate failures, and each needs its own test.

**Tempting mistake:** Checking `length(unique(id)) == nrow(records)` alone. For c("A", NA, "C") unique keeps NA as a value, so the count is 3 and a missing key passes.

**Verify:** `anyDuplicated(records$id)` returns 0 on the starter; changing id to c("B", "A", "A") makes it return 3, the position of the repeat.

### Exercise 4

Diagnose sorting only the amount column in place.

Sort entire rows with an order index.

**Approach:** Compute `order(records$id)` once and use it as a row index with `drop = FALSE`.

**Why it holds here:** The permutation 2, 1, 3 is applied to every column together, so A stays with 10 and B with 20.

**Tempting mistake:** Writing `records$amount <- sort(records$amount)`. The amounts become 10, 20, 30 against ids B, A, C, so B shows 10 with no error, as Example 3 shows for the id column.

**Verify:** In the sorted table `sorted$amount[sorted$id == "A"]` returns 10, and the printed row names read 2, 1, 3.

### Exercise 5

Select zero rows while preserving columns and types.

The result has zero rows and the original schema.

**Approach:** Index rows with `integer(0)` and keep `drop = FALSE`: `records[integer(0), , drop = FALSE]`.

**Why it holds here:** A zero-length row index selects no rows but every column, so id stays character and both numeric columns stay numeric.

**Tempting mistake:** Writing `records[0]`. A single index on a data frame selects columns, so the result keeps all three rows and drops every column, the opposite of what the task asks.

**Verify:** `nrow(empty)` returns 0 and `names(empty)` shows id, amount and amount_with_fee; str reports `chr(0)` for id.

### Exercise 6

Distinguish repeated order IDs from duplicate line IDs.

A multi-line order can repeat OrderID while each LineID must remain unique.

**Approach:** Test uniqueness on the column that defines the table's grain, which is line_id for a lines table.

**Why it holds here:** L1 and L2 are distinct lines that both belong to order O1, so repeated order ids are expected while line ids must not repeat.

**Tempting mistake:** Requiring order_id to be unique, or deduplicating on it. The check rejects a valid two-line order, and deduplication drops L2 and understates the order.

**Verify:** `anyDuplicated(lines$order_id)` returns 2 while `anyDuplicated(lines$line_id)` returns 0.

## What the checks establish

The checks confirm a three row by two column table, a derived fee column reading 22, 12 and 32 in the original row order, ids that are present and unique, an amount sort yielding 10, 20 and 30, an empty selection that keeps the column names, and line ids that are unique while order ids repeat. They do not prove that a key stays unique across future data loads.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
