# r-024: reference reasoning

Run the [complete reference](r-024_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The implementation uses the pinned replacement-method syntax and the S7 NULL validator convention. It separately tests constructor validation, property replacement and a compatibility check inside a multi-argument method. These are different sources of guarantees.

The count operation demonstrates an independent generic with the same public class. The all-empty case is deliberate and preserves units. Class-system interoperability is deferred to explicit adapters; the shared @ notation is not used as evidence of S4 inheritance.

## Explained practice

### Exercise 1

Predict the total of Series(values=c(3,7),unit="ms").

series_total returns c(ms=10).

**Expected evidence:** Named total ms=10.

**Approach:** Construct `Series(values = c(3, 7), unit = "ms")` and call `series_total(x)`. The generic dispatches on x and finds the method registered with `S7::method(series_total, Series)`.

**Why it holds here:** The values are finite and the unit is one nonempty string, so the validator returns NULL and construction succeeds. The method sums 3 and 7 and names the result with the unit, giving c(ms = 10).

**Tempting mistake:** Computing `sum(x@values)` outside the generic. The number is right, but the unit name is lost, so a later comparison with a named total fails and the reader no longer knows the scale.

**Verify:** `identical(series_total(x), c(ms = 10))` returns TRUE.

### Exercise 2

Join that Series to a five-millisecond Series.

The result contains c(3,7,5), has unit ms and total 15.

**Expected evidence:** Three values and total 15.

**Approach:** Call `join_series(x, Series(values = 5, unit = "ms"))`. The generic dispatches on both arguments and the list(Series, Series) method checks units before building a new Series.

**Why it holds here:** Both units are ms, so the values are concatenated in argument order as 3, 7 and 5, and the total is 15. x itself still holds 3 and 7, because the method returns a new object.

**Tempting mistake:** Passing a bare 5 as the second argument. No method is registered for a Series paired with a plain number, so S7 stops instead of guessing that 5 is in milliseconds.

**Verify:** `y@values` returns 3, 7, 5, and `series_total(y)` returns c(ms = 15).

### Exercise 3

Add a series_count generic returning the number of observations.

S7::new_generic("series_count","x") and S7::method(series_count,Series) <- function(x) length(x@values) return 3L for the joined value.

**Expected evidence:** An integer count 3L.

**Approach:** Create the generic with `S7::new_generic("series_count", "x")` and register `S7::method(series_count, Series) <- function(x) length(x@values)`.

**Why it holds here:** The generic dispatches on x alone. S7 validates whenever a Series is constructed or a property is set, so the method can trust its input, and length returns the integer 3L for the joined series.

**Tempting mistake:** Returning `as.numeric(length(x@values))`. It prints 3, but the value is double, so `identical(series_count(y), 3L)` is FALSE and the stated integer contract is broken.

**Verify:** `identical(series_count(y), 3L)` returns TRUE, and `series_count(empty)` returns 0L.

### Exercise 4

Diagnose a validator returning TRUE on success.

The S7 validator must return NULL on success. TRUE belongs to the S4 validity convention taught in r-022.

**Expected evidence:** Use the correct S7 success result.

**Approach:** End the S7 validator with `if (length(problems)) problems else NULL`, returning NULL when the object is valid and a character vector of problems otherwise.

**Why it holds here:** S7 reads NULL as valid and any character result as a list of problems. The S4 validity function in r-022 returns TRUE on success, and the two conventions look alike but are not interchangeable.

**Tempting mistake:** Copying the S4 ending `else TRUE`. S7 stops with a message saying the validator must return NULL or a character, not <logical>, so construction fails for perfectly valid inputs such as 3 and 7 in ms.

**Verify:** `Series(values = c(3, 7), unit = "ms")` returns a Series without error when the validator ends with `else NULL`.

### Exercise 5

Test invalid property replacement and verify retained state.

Replacing unit with character(0) fails; the previous "ms" unit remains.

**Expected evidence:** Error plus unchanged property.

**Approach:** Run `x@unit <- character(0)` inside a handler expecting "nonempty string", then read `x@unit` again.

**Why it holds here:** S7 runs the validator whenever a property is replaced. character(0) has the right class, but the validator rejects it, and because the assignment fails, x keeps its previous unit.

**Tempting mistake:** Assuming S7 behaves like the S4 class in r-022, where `@<-` skips validity. Skipping this test would leave the most important difference between the two systems unchecked.

**Verify:** The handler returns a message containing "unit must be one nonempty string", and `x@unit` still returns "ms".

### Exercise 6

Explain why @ access does not make an S7 object an S4 object.

Use the public S7 interface and explicit adapters rather than assuming S4 slot introspection or methods apply.

**Expected evidence:** No inferred cross-system inheritance.

**Approach:** Work with a Series through its S7 constructor, properties and generics, and write an explicit adapter when S4 code needs the same data.

**Why it holds here:** `@` is shared syntax, but S7 resolves it through its own property system. S4 methods such as combine_measure from r-022 are registered for FormalMeasure, so they have no method for a Series.

**Tempting mistake:** Passing a Series to combine_measure because both objects answer `@values`. Dispatch fails, and if it did not, the S4 validity rules would never have been checked for this object.

**Verify:** `S7::S7_inherits(x, Series)` returns TRUE, and `class(x)` shows "Series" and "S7_object", not FormalMeasure.

## What the checks establish

The assertions confirm that an invalid replacement fails with the expected message, that the series totals `c(ms = 10)`, that joining a 5 ms series gives values 3, 7 and 5 and a total of 15, that the new count generic returns 3L, that the unit stays ms after a failed replacement, and that an empty series counts 0 and totals 0. They do not test dispatch on classes beyond `Series`.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
