# r-006: reference reasoning

Run the [complete reference](r-006_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

A finite-value mask is stricter than a missing-value mask. It rejects infinities as well as missing and undefined results.

The reporting policy preserves no observed sum instead of interpreting the empty-sum arithmetic convention as a measurement.

In the worked summary, if (observed == 0) chooses one result when the scalar condition is TRUE; else supplies the other result. Both branches use the same reported_sum name, so the no-observation policy is visible in the returned value. Chapter r-011 develops branching and loops more fully.

## Explained practice

### Exercise 1

Predict length(c(NULL, NA_real_)).

The length is one.

**Approach:** Count what each argument contributes to `c()`: NULL contributes nothing, and NA_real_ contributes one slot.

**Why it holds here:** NULL means absence of an object, so combining it adds no element. NA_real_ is a double whose value is unknown, and it still occupies a position.

**Tempting mistake:** Predicting 2 by treating NULL as one more missing entry, or 0 by assuming NA vanishes like NULL. Both blur the line between no element and an unknown element.

**Verify:** The reference asserts `length(c(NULL, NA_real_)) == 1L`, and `print()` shows `[1] NA`.

### Exercise 2

Add zero to an all-missing measurement vector.

The observed count becomes one and its observed mean is zero.

**Approach:** Append the zero, then count observed entries with `sum(!is.na(x))` and summarize with `mean(x, na.rm = TRUE)`.

**Why it holds here:** Zero is a measurement, not a gap. After removing the two unknowns one value remains, so the observed count is 1 and the observed mean is 0.

**Tempting mistake:** Treating zero as missing, for example by recoding it to NA. Then nothing is observed and `mean(x, na.rm = TRUE)` returns NaN, erasing the one real reading.

**Verify:** `sum(!is.na(x))` returns 1 and `mean(x, na.rm = TRUE)` returns 0, both asserted in the reference.

### Exercise 3

Construct a finite-only mask for c(2, Inf, NA,4).

is.finite retains two and four.

**Approach:** Build the mask with `is.finite(x)` and index with it.

**Why it holds here:** For c(2, Inf, NA, 4), `is.finite` is TRUE only for 2 and 4. It is FALSE for Inf and for NA, so one predicate removes both exceptional kinds.

**Tempting mistake:** Using `!is.na(x)` keeps Inf, so the selection is 2, Inf, 4 and any total over it becomes Inf.

**Verify:** The reference asserts `identical(x[is.finite(x)], c(2, 4))`, and `sum()` of that selection returns 6.

### Exercise 4

Diagnose calling an all-missing sum a measured zero.

Report no observations and an explicit missing summary under the stated policy.

**Approach:** Check the observed count before summing. When nothing is observed, report NA together with the zero count.

**Why it holds here:** With both entries missing, `na.rm = TRUE` leaves an empty vector, and the sum of an empty vector is 0 by convention. That 0 describes no measurement at all.

**Tempting mistake:** Publishing `sum(all_missing, na.rm = TRUE)` as a total of 0. A reader would assume someone measured and found nothing.

**Verify:** In the reference, `is.na(reported)` is TRUE, while `sum(all_missing, na.rm = TRUE)` returns 0 for contrast.

### Exercise 5

Distinguish NA from NaN.

is.na is true for both, but is.nan is true only for NaN.

**Approach:** Ask two separate questions: `is.na()` for any missing or undefined value and `is.nan()` only for undefined arithmetic.

**Why it holds here:** NaN arises from operations such as 0 / 0; NA marks a value that was never recorded. `is.na(NaN)` is TRUE, but `is.nan(NA_real_)` is FALSE.

**Tempting mistake:** Counting undefined results with `is.na()`. On the starter vector that reports 2, mixing the unrecorded value with the undefined one.

**Verify:** On the starter vector, `sum(is.na(x))` returns 2 and `sum(is.nan(x))` returns 1.

### Exercise 6

Document a division-by-zero policy in a data pipeline.

Validate the denominator and retain a meaningful signal instead of silently replacing every exceptional result with zero.

**Approach:** Write the policy into a function: reject a zero or non-finite denominator by returning NA_real_, otherwise divide.

**Why it holds here:** Without the guard, `1 / 0` returns Inf, which passes an `is.na` check and inflates any later mean. Returning NA keeps the case visible as undefined.

**Tempting mistake:** Replacing every non-finite ratio with 0. That claims a measured zero rate for a case that had no denominator.

**Verify:** The reference checks that `ratio(1, 0)` returns NA and `ratio(4, 2)` returns 2.

## What the checks establish

The checks pin that `c(NULL, NA_real_)` has length one because NULL contributes nothing, that a vector with one known zero has an `na.rm` mean of 0, that `is.finite()` keeps 2 and 4, that `is.na()` is TRUE for NA and NaN while `is.nan()` is TRUE only for NaN, and that the guarded ratio returns NA for a zero denominator. They do not decide which missing values your report should count.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
