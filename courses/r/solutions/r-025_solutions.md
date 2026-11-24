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

**Approach:** Pass the values and unit through `measurement_record()` to validate and store them as doubles, then call `record_mean()`.

**Why it holds here:** The mean of 2 and 4 is 3, there are two observations, and the unit is ms, so the result is list(mean = 3, count = 2L, unit = "ms"), with every field the contract names.

**Tempting mistake:** Returning only `mean(values)`. A bare 3 cannot be told apart from a 3 second mean over two hundred observations, so the consumer loses both scale and sample size.

**Verify:** `identical(record_mean(records[[1]]), list(mean = 3, count = 2L, unit = "ms"))` returns TRUE.

### Exercise 2

Write an R6 adapter using public values() and unit() methods.

Pass x$values() and x$unit() through measurement_record; verify the numeric record can change without mutating the source.

**Expected evidence:** The adapted record satisfies the public contract.

**Approach:** Write `from_r6 <- function(x) measurement_record(x$values(), x$unit())` so the adapter uses only the Store's public methods.

**Why it holds here:** Store keeps its data in private fields that only its methods can read. The record is a plain list holding copies of the numbers, so editing the record cannot reach back into the Store.

**Tempting mistake:** Reading the private environment through R6 internals. It may work today, but renaming a private field breaks the adapter, which the public methods were written to prevent.

**Verify:** After `copy$values[[1]] <- 100`, `r6$values()[[1]]` still returns 2.

### Exercise 3

Write an S7 adapter using its declared properties.

Validate the expected S7 class with S7::S7_inherits, then pass values and unit to measurement_record.

**Expected evidence:** S7 and other valid inputs have equal records.

**Approach:** Check `S7::S7_inherits(x, Series)` first, then pass `x@values` and `x@unit` to `measurement_record()`.

**Why it holds here:** The class check confirms which object system and class the adapter supports before any property is read, and the resulting record is identical to those from the S3, S4 and R6 adapters.

**Tempting mistake:** Reading `x@values` with no class check. The S4 object s4 also answers `@values`, so `from_s7(s4)` would succeed and the adapter would quietly accept a second contract.

**Verify:** `all(vapply(records, identical, logical(1), records[[1]]))` returns TRUE, and `from_s7(s4)` stops at the class check.

### Exercise 4

Diagnose unclass on an object whose numbers are seconds while callers assume milliseconds.

Removing class does not multiply values or preserve unit semantics. Require explicit source unit and conversion, or reject the mismatch.

**Expected evidence:** No silent scale change.

**Approach:** Require each record to state its unit, and either convert explicitly, multiplying seconds by 1000 and setting unit ms, or reject a unit the caller did not ask for.

**Why it holds here:** unclass removes only the class attribute. Values of 2 and 4 seconds remain the numbers 2 and 4, so a caller that assumes milliseconds reads them as a thousand times smaller.

**Tempting mistake:** Passing `unclass(x)$values` to code that expects milliseconds. The mean of 3 is reported as 3 ms when it is really 3000 ms, and nothing warns.

**Verify:** `unclass(x)$values` returns the same numbers as `x$values`, which shows that no conversion took place.

### Exercise 5

Change the plotted latency values and inspect the built y coordinates.

Using c(4,7,9) gives built y coordinates 4,7,9. The assertion says nothing about screen rendering.

**Expected evidence:** Exact new coordinates and bounded interpretation.

**Approach:** Build the plot from data with latency 4, 7 and 9, call `ggplot2::ggplot_build(plot)$data[[1]]`, and compare its x and y columns with the input.

**Why it holds here:** geom_point uses the identity stat, so the built layer holds the mapped values unchanged. This checks the aesthetic mapping, not how the points look on a screen.

**Tempting mistake:** Checking `plot$data$latency`. The input frame is stored there whatever the mapping says, so a plot with `y = time` by mistake would still pass.

**Verify:** `layer$y` returns 4, 7, 9, and `layer$x` returns 1, 2, 3.

### Exercise 6

Test an empty record and explain why its mean is missing.

Return count 0, mean NA_real_ and the declared unit; do not manufacture a zero mean.

**Expected evidence:** An explicit empty-input result.

**Approach:** Build `measurement_record(numeric(0), "ms")`, call `record_mean()` and check all three fields.

**Why it holds here:** No observations means there is no observed average, so the function returns NA_real_ explicitly, with count 0L explaining why and the unit still declared. mean of an empty vector would return NaN instead.

**Tempting mistake:** Reporting a mean of 0. A dashboard would show an empty period as zero latency, the best possible value, when it actually has no data.

**Verify:** `empty$count` returns 0L, `is.na(empty$mean)` returns TRUE, and `empty$unit` returns "ms".

## What the checks establish

The reference makes 9 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
