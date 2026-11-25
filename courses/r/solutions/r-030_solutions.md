# r-030: reference reasoning

Run the [complete reference](r-030_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The capstone reference checks independent arithmetic as well as the representation invariant. The equal-length rule prevents recycling; uniqueness prevents a repeated identifier from contributing twice; unit compatibility prevents a silent scale change. Missing observations remain visible in the summary ledger.

The forged-object test establishes why class labels alone are insufficient. The unchanged-input assertions support the chosen value-object interface, while the proposed NAMESPACE lines identify the optional package boundary. No package has been installed or published by this script, and passing its checks does not make missingness ignorable or supply a causal design.

## Explained practice

### Exercise 1

Predict the summary of values c(2,NA,6) with three unique IDs.

Rows 3, observed 2, missing 1, mean 4, with the declared unit.

**Expected evidence:** A complete denominator ledger.

**Approach:** Count all rows, then the non-missing values, then average only the observed ones: 3 rows, 2 observed, 1 missing, mean of 2 and 6.

**Why it holds here:** summary.metric_batch uses `!is.na(x$values)` as its denominator, so the mean is 8 divided by 2, which is 4, and the missing value stays visible in its own count with unit ms.

**Tempting mistake:** Dividing the observed sum by all 3 rows, giving 8/3. The NA is silently treated as zero and the average drops by a third.

**Verify:** `identical(s, list(rows = 3L, observed = 2L, missing = 1L, mean = 4, unit = "ms"))` returns TRUE.

### Exercise 2

Add one new eight-millisecond record and recompute the summary.

The combined batch has four rows, three observed values, one missing value and mean 16/3 ms.

**Expected evidence:** Known arithmetic 16/3.

**Approach:** Build `metric_batch("d", 8, "ms")`, combine it with a, and summarize the new batch.

**Why it holds here:** combine_batches concatenates ids and values, so the observed values are 2, 6 and 8 with sum 16 over 3 observed, about 5.33 ms. The row count is 4 and one value is still missing.

**Tempting mistake:** Averaging the two batch means, 4 and 8, to get 6. That gives the one value batch the same weight as the two observed values in a.

**Verify:** `isTRUE(all.equal(summary(b)$mean, 16 / 3))` returns TRUE, and `summary(b)$rows` returns 4L.

### Exercise 3

Independently implement and test the duplicate-ID and equal-length constructor rules.

Duplicate IDs and vectors of unequal length each raise their specific contract error.

**Expected evidence:** Two distinct rejected input shapes.

**Approach:** Check ids for type, NA, empty strings and duplicates, then check equal lengths, all before `structure()` attaches the class.

**Why it holds here:** `c("a", "a")` fails the uniqueness rule, and `c("a", "b")` with a single value fails the length rule. Each shape reaches its own message, so neither produces a labeled object.

**Tempting mistake:** Skipping the length check. A batch with two ids and one value would report rows 2, observed 1 and missing 0, a ledger whose parts do not add up.

**Verify:** assert_error matches "unique nonempty" for the duplicates and "equal length" for the short vector.

### Exercise 4

Diagnose returning zero for an all-missing batch.

Return mean NA_real_ and observed 0 while retaining the missing count and unit. Zero is a measured value, not absence of information.

**Expected evidence:** Explicit all-missing behavior.

**Approach:** Return mean `NA_real_` with observed 0, keeping the missing count and the unit.

**Why it holds here:** With values NA and NA, nothing was measured, so no mean exists. The `if (any(observed))` guard also avoids `mean(numeric(0))`, which returns NaN, and the empty batch gets rows 0 and mean NA the same way.

**Tempting mistake:** Returning 0. A reader sees a measured latency of 0 ms, and averaging it with other batches pulls their result down.

**Verify:** `is.na(summary(all_missing)$mean)` returns TRUE, and `summary(all_missing)$missing` returns 2L.

### Exercise 5

Test a forged class object and incompatible-unit combination.

A forged Inf value fails finite-or-NA validation; a valid seconds batch cannot combine with milliseconds without an explicit conversion. Original inputs remain unchanged.

**Expected evidence:** Rejected boundaries without mutation.

**Approach:** Revalidate inside every public function, then compare units with identical() and stop on a mismatch.

**Why it holds here:** The forged object skips the constructor, but summary calls validate_batch, which reruns it and rejects Inf. A seconds batch fails the unit check, and a's id "a" repeated in another batch fails uniqueness.

**Tempting mistake:** Checking only `inherits(x, "metric_batch")`. The forged batch would report mean Inf, and concatenating 1 s with values in ms would mix scales a thousand times apart.

**Verify:** assert_error matches "incompatible batch units", and `identical(a, before)` returns TRUE.

### Exercise 6

Write the package interface and state the inferential limit of a passing reference.

Export metric_batch and combine_batches; register S3method(summary,metric_batch); keep helpers internal. Run package checks in a separate multi-file project. These descriptive checks do not establish representativeness or causal effects.

**Expected evidence:** A concrete continuation and bounded scientific claim.

**Approach:** Export metric_batch and combine_batches, register `S3method(summary,metric_batch)`, and keep validate_batch internal. State that passing checks describe these fixtures only.

**Why it holds here:** Registration lets `summary()` dispatch to the method without exporting it. validate_batch is a helper, so leaving it out keeps the interface small.

**Tempting mistake:** Using an exportPattern that matches every name, which publishes validate_batch too, or saying the passing checks show latency improved.

**Verify:** `grepl("validate_batch", namespace, fixed = TRUE)` returns FALSE for all three lines.

## What the checks establish

The assertions confirm a summary of 3 rows, 2 observed, 1 missing and mean 4 in ms, an extended batch of 4 rows with mean 16/3, an all-missing batch with an NA mean, an empty batch with zero rows and an NA mean, an unchanged original after extension, a rejected forged or incompatible object, and a NAMESPACE that keeps the validator unexported. They do not establish any inference about the population behind these values.

The reference makes 8 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
