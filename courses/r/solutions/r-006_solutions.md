# r-006: reference reasoning

Use the [complete reference](r-006_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

A finite-value mask is stricter than a missing-value mask. It rejects infinities as well as missing and undefined results.

The reporting policy preserves no observed sum instead of interpreting the empty-sum arithmetic convention as a measurement.

In the worked summary, if (observed == 0) chooses one result when the scalar condition is TRUE; else supplies the other result. Both branches use the same reported_sum name, so the no-observation policy is visible in the returned value. Chapter r-011 develops branching and loops more fully.

## Explained practice

### Exercise 1

Predict length(c(NULL, NA_real_)).

The length is one.

**Expected evidence:** The length is one.

### Exercise 2

Add zero to an all-missing measurement vector.

The observed count becomes one and its observed mean is zero.

**Expected evidence:** The observed count becomes one and its observed mean is zero.

### Exercise 3

Construct a finite-only mask for c(2, Inf, NA,4).

is.finite retains two and four.

**Expected evidence:** is.finite retains two and four.

### Exercise 4

Diagnose calling an all-missing sum a measured zero.

Report no observations and an explicit missing summary under the stated policy.

**Expected evidence:** Report no observations and an explicit missing summary under the stated policy.

### Exercise 5

Distinguish NA from NaN.

is.na is true for both, but is.nan is true only for NaN.

**Expected evidence:** is.na is true for both, but is.nan is true only for NaN.

### Exercise 6

Document a division-by-zero policy in a data pipeline.

Validate the denominator and retain a meaningful signal instead of silently replacing every exceptional result with zero.

**Expected evidence:** Validate the denominator and retain a meaningful signal instead of silently replacing every exceptional result with zero.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
