# r-030: reference reasoning

Use the [complete reference](r-030_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The capstone reference checks independent arithmetic as well as the representation invariant. The equal-length rule prevents recycling; uniqueness prevents a repeated identifier from contributing twice; unit compatibility prevents a silent scale change. Missing observations remain visible in the summary ledger.

The forged-object test establishes why class labels alone are insufficient. The unchanged-input assertions support the chosen value-object interface, while the proposed NAMESPACE lines identify the optional package boundary. No package has been installed or published by this script, and passing its checks does not make missingness ignorable or supply a causal design.

## Explained practice

### Exercise 1

Predict the summary of values c(2,NA,6) with three unique IDs.

Rows 3, observed 2, missing 1, mean 4, with the declared unit.

**Expected evidence:** A complete denominator ledger.

### Exercise 2

Add one new eight-millisecond record and recompute the summary.

The combined batch has four rows, three observed values, one missing value and mean 16/3 ms.

**Expected evidence:** Known arithmetic 16/3.

### Exercise 3

Independently implement and test the duplicate-ID and equal-length constructor rules.

Duplicate IDs and vectors of unequal length each raise their specific contract error.

**Expected evidence:** Two distinct rejected input shapes.

### Exercise 4

Diagnose returning zero for an all-missing batch.

Return mean NA_real_ and observed 0 while retaining the missing count and unit. Zero is a measured value, not absence of information.

**Expected evidence:** Explicit all-missing behavior.

### Exercise 5

Test a forged class object and incompatible-unit combination.

A forged Inf value fails finite-or-NA validation; a valid seconds batch cannot combine with milliseconds without an explicit conversion. Original inputs remain unchanged.

**Expected evidence:** Rejected boundaries without mutation.

### Exercise 6

Write the package interface and state the inferential limit of a passing reference.

Export metric_batch and combine_batches; register S3method(summary,metric_batch); keep helpers internal. Run package checks in a separate multi-file project. These descriptive checks do not establish representativeness or causal effects.

**Expected evidence:** A concrete continuation and bounded scientific claim.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
