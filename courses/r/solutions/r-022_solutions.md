# r-022: reference reasoning

Use the [complete reference](r-022_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference tests two dispatch paths and two kinds of domain failure. An incompatible unit pair is structurally valid and matches the formal signature, but still fails the operation's compatibility rule. An empty unit passes the slot's character type and fails validObject.

The conversion function makes the scale factor visible and returns a newly validated value. The assertion about the unchanged seconds object separates conversion from in-place mutation. This is a checked local class definition, not an installed package or a claim that every S4 slot mutation automatically runs all invariants.

## Explained practice

### Exercise 1

Predict the result of combining c(1,3) ms with 5 ms.

The result is a FormalMeasure containing c(1,3,5), unit ms.

**Expected evidence:** Three observations in original order.

**Approach:** Trace the dispatch on both arguments: x and y are FormalMeasure objects, so the (FormalMeasure, FormalMeasure) method runs, validates both, compares units and builds a new object from `c(x@values, y@values)`.

**Why it holds here:** Both units are "ms", so the method concatenates the observations in argument order, 1, 3 and then 5, and the new object passes validity again on construction.

**Tempting mistake:** Expecting arithmetic. `c(1, 3) + 5` recycles the 5 and gives 6 and 8, but combine_measure joins observations; it never adds them.

**Verify:** `z@values` returns 1, 3, 5, and `z@unit` returns "ms".

### Exercise 2

Change the second input to seconds and test the failure.

The typed-pair method raises incompatible units. Dispatch is not a unit conversion system.

**Expected evidence:** The incompatible-units error.

**Approach:** Build `seconds <- new("FormalMeasure", values = 2, unit = "s")` and call `combine_measure(x, seconds)` inside a handler that expects "incompatible units".

**Why it holds here:** Both arguments are still FormalMeasure objects, so the same method is selected; dispatch looks at classes, not slot contents. The `identical(x@unit, y@unit)` check inside the method is what rejects ms against s.

**Tempting mistake:** Expecting dispatch to choose another method or to convert. Without the unit check the result would be 1, 3 and 2 labeled ms, treating two seconds as two milliseconds, an error by a factor of 1000.

**Verify:** `tryCatch(combine_measure(x, seconds), error = conditionMessage)` returns "incompatible units".

### Exercise 3

Construct a new object with an infinite measurement.

new invokes validity and rejects the nonfinite value.

**Expected evidence:** Finite-vector error.

**Approach:** Call `new("FormalMeasure", values = Inf, unit = "ms")` and capture the error message.

**Why it holds here:** The slot type is numeric and Inf is numeric, so the slot check passes. new() then runs the function registered with setValidity, which finds a nonfinite value and returns its message, so construction stops.

**Tempting mistake:** Relying on `slots = c(values = "numeric")` as the guard. Inf, negative Inf and NaN are all numeric, so a type-only class would accept them and every later total would be infinite or NaN.

**Verify:** The captured message contains "values must be a finite vector" after the invalid class prefix.

### Exercise 4

Diagnose a direct x@unit <- character(0) assignment.

Run validObject before exposing the changed value; the domain check fails. Prefer a validated replacement interface.

**Expected evidence:** A semantic validity failure.

**Approach:** After a direct slot assignment, call `validObject(broken)` before the object leaves the code that changed it, and prefer a replacement function that validates for callers.

**Why it holds here:** `@<-` checks only that the new value has the slot's class. character(0) is character, so the assignment succeeds, and only the validity function notices that the unit is not one string.

**Tempting mistake:** Assuming `@<-` runs validity. Code that reads `broken@unit` without validating gets a zero-length value, and `paste(2, broken@unit)` quietly returns "2 " with the unit missing.

**Verify:** `tryCatch(validObject(broken), error = conditionMessage)` returns a message containing "unit must be one nonempty string".

### Exercise 5

Test the FormalMeasure,numeric method separately.

combine_measure(x,2) raises the no-declared-unit error rather than accepting it as milliseconds.

**Expected evidence:** Distinct explicit rejection path.

**Approach:** Call `combine_measure(x, 2)` on its own and assert its specific message, separately from the unit mismatch test.

**Why it holds here:** The signature (FormalMeasure, numeric) matches exactly, so that method runs and stops with "numeric input has no declared unit". It is a different branch from the mismatch check, so it needs its own test.

**Tempting mistake:** Treating the bare 2 as milliseconds because x is in ms. If that method were missing, dispatch would fail with a missing method error, and a test that matched any error would pass for the wrong reason.

**Verify:** `tryCatch(combine_measure(x, 2), error = conditionMessage)` returns "numeric input has no declared unit".

### Exercise 6

Design a safe seconds-to-milliseconds conversion boundary.

A dedicated conversion function checks the original unit, multiplies values by 1000, sets unit ms, and constructs a validated new FormalMeasure. It must reject unknown units.

**Expected evidence:** Two seconds converts to 2000 ms without changing the input.

**Approach:** Write `to_ms()` to validate its input, require unit "s", multiply the values by 1000 and construct a new FormalMeasure with unit "ms".

**Why it holds here:** A conversion must change values and unit together. Building a new object runs validity again, and the input is never modified, so 2 seconds becomes 2000 ms while seconds still holds 2 and "s".

**Tempting mistake:** Changing only the unit with `seconds@unit <- "ms"`. That relabels 2 as 2 ms, wrong by a factor of 1000, and the same mistake repeats if a ms object is converted without the unit check.

**Verify:** `to_ms(seconds)@values` returns 2000, `seconds@values` still returns 2, and `to_ms(x)` stops with "conversion requires seconds".

## What the checks establish

The reference makes 3 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
