# r-004: reference reasoning

Run the [complete reference](r-004_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The mask explicitly excludes missing amounts and separately tests the threshold. Unknown values are counted, not interpreted as measured failures.

The first condition prevents an invalid extraction from an empty vector. The truth-table checks explain when uncertainty does and does not affect the combined answer.

## Explained practice

### Exercise 1

Predict TRUE & NA and FALSE & NA.

The first is NA; the second is FALSE.

**Approach:** For each expression, ask whether the known operand already decides a conjunction, then evaluate both in one vector.

**Why it holds here:** A FALSE side makes any and FALSE whatever the unknown turns out to be, so FALSE & NA is FALSE. A TRUE side leaves the answer depending on the unknown, so TRUE & NA stays NA, which the reference asserts with is.na().

**Tempting mistake:** Treating NA as if it were FALSE predicts FALSE for both. The opposite shortcut, assuming any NA poisons the result, predicts NA for both. Each gets one of the two cases wrong.

**Verify:** `print(c(TRUE & NA, FALSE & NA))` shows `[1]    NA FALSE`.

### Exercise 2

Change the threshold from ten to fifteen.

Only the amount twenty remains.

**Approach:** Keep the missingness guard and change only the threshold: `x[!is.na(x) & x >= 15]`.

**Why it holds here:** Among 5, 12, NA and 20, only 20 reaches fifteen. The guard drops the unknown third amount under the same policy as before, so the threshold edit cannot quietly change how missing values are handled.

**Tempting mistake:** Dropping the guard and writing `x[x >= 15]`. The NA comparison selects an NA element, so the result is NA and 20, a length-two vector with a phantom amount in it.

**Verify:** The reference asserts `identical(x[!is.na(x) & x >= 15], 20)`, so the result has length 1 and value 20.

### Exercise 3

Construct a mask for known amounts from ten through twenty inclusive.

Use !is.na(x) & x >= 10 & x <= 20.

**Approach:** Combine three conditions with vectorized &: known, at least ten, and at most twenty.

**Why it holds here:** The upper bound is inclusive, so 20 stays in, and 5 falls below the lower bound. The selection is 12 and 20, matching the starter data exactly.

**Tempting mistake:** Writing `x < 20` drops the boundary amount and leaves only 12. Using `&&` instead of `&` is also wrong here: it expects single values, and current R stops with an error about a length greater than one rather than building a mask.

**Verify:** `x[mask]` returns 12 and 20, and `sum(mask)` counts 2 TRUE entries.

### Exercise 4

Diagnose x == NA.

Use is.na(x) to test missingness.

**Approach:** Replace the equality test with `is.na(x)`, which answers the question asked of every element.

**Why it holds here:** `x == NA` compares each amount with an unknown, so even the known values 5, 12 and 20 give NA. The result carries no information about which position is missing.

**Tempting mistake:** Using `which(x == NA)` to locate missing values. `which()` skips NA entries, so it returns `integer(0)` and claims there is nothing missing while the third amount is NA.

**Verify:** `is.na(x)` prints FALSE FALSE TRUE FALSE, the value the reference checks, while `sum(x == NA)` returns NA.

### Exercise 5

Guard an empty vector before extracting its first element.

length(x) > 0 && x[[1]] > 0 safely returns FALSE for an empty vector.

**Approach:** Put the length test first and join it with `&&`, so the extraction only runs when an element exists.

**Why it holds here:** `&&` evaluates left to right and stops at the first FALSE. For `numeric(0)` the length test is FALSE, so `empty[[1]]` is never evaluated and the whole expression is FALSE.

**Tempting mistake:** Using single `&` evaluates both sides, and `empty[[1]]` fails with a subscript out of bounds error. Writing `empty[1] > 0` avoids the error but returns `logical(0)`, which breaks any `if` that uses it.

**Verify:** The guarded expression returns FALSE with no error, which is exactly what the reference wraps in `stopifnot(!(...))`.

### Exercise 6

Separate an all-known claim from all(..., na.rm=TRUE).

Report missingness and state that the reduced claim concerns observed predicates only.

**Approach:** Report two things: whether the claim holds for observed predicates, and how many predicates were unknown.

**Why it holds here:** `all(c(TRUE, NA))` is NA because the unknown entry could be FALSE. With `na.rm = TRUE` the answer becomes TRUE, but only about the known entries. On the starter amounts, `all(amount >= 5)` is NA for the same reason.

**Tempting mistake:** Quoting the `na.rm = TRUE` result as "every amount is at least 5". The third amount was never measured, so that sentence claims more than the data shows.

**Verify:** The reference checks `is.na(all(c(TRUE, NA)))` and `isTRUE(all(c(TRUE, NA), na.rm = TRUE))`; `sum(is.na(amount))` reports the 1 unknown to cite alongside.

## What the checks establish

The assertions pin three-valued logic directly: `TRUE & NA` is NA while `FALSE & NA` is FALSE, a mask built with `!is.na()` keeps only the known 20 at or above 15, the inclusive mask selects 12 and 20, `&&` short-circuits safely on an empty vector, and `all()` returns NA unless `na.rm = TRUE`. They do not show that dropping unknown amounts is the right policy for a real report.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
