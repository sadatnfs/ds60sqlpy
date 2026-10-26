# r-025: reference reasoning

Use the [complete reference](r-025_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

All four adapters converge on one ordinary record. The equal-record assertion compares values, type normalization and units, rather than merely comparing a final mean. The R6 copy test is intentionally limited to a returned numeric vector.

The ggplot2 test exercises a public builder and checks actual layer coordinates. It remains valid without relying on the central plot object's internal S3 or S7 layout. Empty values and nonfinite values take different paths under the declared contract: one yields a missing summary, the other is rejected.

## Explained practice

### Exercise 1

Predict the record summary for values c(2,4) and unit ms.

The result is list(mean=3,count=2L,unit="ms").

**Expected evidence:** All three fields are preserved.

### Exercise 2

Write an R6 adapter using public values() and unit() methods.

Pass x$values() and x$unit() through measurement_record; verify the numeric record can change without mutating the source.

**Expected evidence:** The adapted record satisfies the public contract.

### Exercise 3

Write an S7 adapter using its declared properties.

Validate the expected S7 class with S7::S7_inherits, then pass values and unit to measurement_record.

**Expected evidence:** S7 and other valid inputs have equal records.

### Exercise 4

Diagnose unclass on an object whose numbers are seconds while callers assume milliseconds.

Removing class does not multiply values or preserve unit semantics. Require explicit source unit and conversion, or reject the mismatch.

**Expected evidence:** No silent scale change.

### Exercise 5

Change the plotted latency values and inspect the built y coordinates.

Using c(4,7,9) gives built y coordinates 4,7,9. The assertion says nothing about screen rendering.

**Expected evidence:** Exact new coordinates and bounded interpretation.

### Exercise 6

Test an empty record and explain why its mean is missing.

Return count 0, mean NA_real_ and the declared unit; do not manufacture a zero mean.

**Expected evidence:** An explicit empty-input result.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
