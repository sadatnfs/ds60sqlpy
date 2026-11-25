# r-021: reference reasoning

Run the [complete reference](r-021_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference separates assembly, validation and dispatch, so each failed input has a stated cause. The matrix case is numeric but has a shape that the vector contract excludes. The NA case demonstrates a declared policy rather than accidental na.rm behavior.

The count generic is an independent operation with the same object invariant. Its default rejection prevents unrelated values from silently acquiring domain meaning. Copy assertions establish behavior for the actual numeric-list representation. They are not a proof that all S3 objects are immutable or that package registration has already occurred.

## Explained practice

### Exercise 1

Trace measurement_total(measurement(c(3,7), "ms")).

UseMethod selects measurement_total.measurement; it returns c(ms=10).

**Expected evidence:** Named total ms=10.

**Approach:** Follow the call in order: measurement() builds the list and validates it, UseMethod reads `class(x)`, finds "measurement" and runs measurement_total.measurement, which validates again and returns `setNames(sum(x$values), x$unit)`.

**Why it holds here:** 3 and 7 are finite and "ms" is one nonempty string, so both validator checks pass. sum gives 10, and setNames attaches the unit, so the result is the named value c(ms = 10) rather than a bare number.

**Tempting mistake:** Expecting a bare 10, or the default method. The default runs only when no class matches, and a total without its name loses the unit, so `identical(result, 10)` is FALSE.

**Verify:** `identical(measurement_total(x), c(ms = 10))` returns TRUE, and `names(measurement_total(x))` returns "ms".

### Exercise 2

Add one observation five to the input and check that the earlier object is unchanged.

measurement(c(x$values,5), x$unit) has total 15; x retains total 10.

**Expected evidence:** Totals 10 and 15 with the same unit.

**Approach:** Build `y <- measurement(c(x$values, 5), x$unit)` so the new observation goes through the same constructor and validator, then total both objects.

**Why it holds here:** Constructing a new object never touches x, so x keeps 3 and 7. y holds 3, 7 and 5 with the same unit, so its total is 15 ms while x still totals 10 ms.

**Tempting mistake:** Writing `x$values <- c(x$values, 5)`. That rebinds x itself, so the earlier total of 10 is gone, and it also skips the validator, so a nonfinite addition would not be caught.

**Verify:** `measurement_total(x)` returns c(ms = 10), and `measurement_total(y)` returns c(ms = 15).

### Exercise 3

Implement an observed-count generic for measurement objects.

measurement_count uses UseMethod and its measurement method returns length(validate_measurement(x)$values). The three-observation object returns 3L.

**Expected evidence:** Count 3L and explicit default rejection.

**Approach:** Define `measurement_count <- function(x, ...) UseMethod("measurement_count")`, a measurement method returning `length(validate_measurement(x)$values)`, and a default method that stops.

**Why it holds here:** A separate generic keeps counting distinct from totaling, and validating inside the method rejects forged objects. length returns an integer, so the three observations in y give 3L.

**Tempting mistake:** Calling `length(y)` directly. y is a list with two elements, values and unit, so the result is 2 no matter how many observations it holds.

**Verify:** `identical(measurement_count(y), 3L)` returns TRUE, and `measurement_count(1)` stops with the message "unsupported count input".

### Exercise 4

Diagnose structure(list(values=c(1,Inf),unit="ms"), class="measurement").

The object dispatches as a measurement but violates the finite-vector invariant. The public operation must reject it.

**Expected evidence:** A matching finite-vector validation error.

**Approach:** Treat the object as forged: call `measurement_total()` on it and expect the validator's error, because the method revalidates before summing.

**Why it holds here:** structure() only sets the class attribute; it checks nothing. Dispatch therefore selects the measurement method, and only the validator call inside that method sees Inf and stops.

**Tempting mistake:** Trusting `inherits(x, "measurement")` as proof of validity. A method that summed directly would return c(ms = Inf), and that infinite total would flow into every average and report built on it.

**Verify:** `tryCatch(measurement_total(forged), error = conditionMessage)` returns "values must be a finite numeric vector".

### Exercise 5

Define the empty-vector and empty-unit cases.

measurement(numeric(0),"ms") has total 0 and count 0; an empty unit string is rejected.

**Expected evidence:** Zero total; malformed unit rejected.

**Approach:** Construct `measurement(numeric(0), "ms")` and check its total and count, then construct `measurement(1, "")` and expect a rejection.

**Why it holds here:** numeric(0) is numeric, has no dim and contains no nonfinite value, so the validator accepts it; sum returns 0 and length returns 0L. The unit check requires nzchar, so the empty string fails.

**Tempting mistake:** Adding a rule that values must be nonempty. A period with no observations would then raise an error, although a total of 0 ms is a correct answer for it.

**Verify:** `measurement_total(empty)` returns c(ms = 0), `measurement_count(empty)` returns 0L, and `measurement(1, "")` stops with "unit must be one nonempty string".

### Exercise 6

Explain whether a measurement containing an environment would have the same copy guarantee.

An environment can be shared across list copies. The current constructor excludes such values, so its tested numeric representation has a narrower value-semantics claim.

**Expected evidence:** State the representation-specific limit.

**Approach:** Separate the list container, which is copied when modified, from any component that is itself a reference, and state the copy guarantee only for the numeric representation the constructor accepts.

**Why it holds here:** In the reference, `copy$values[[1]] <- 9` leaves x at 3, because changing a numeric component duplicates it. An environment stored in a list is not duplicated, so both copies hold the same one, and a change through either is seen by both.

**Tempting mistake:** Claiming value semantics for every measurement. Adding a cache environment field later would break the claim without any error.

**Verify:** `x$values[[1]]` still returns 3 after the copy is set to 9, while for a list field holding an environment `identical(copy$env, x$env)` returns TRUE after copying.

## What the checks establish

The assertions confirm that malformed input raises a diagnostic matching the expected text, that the total of 3 and 7 is `c(ms = 10)`, that a new object with 5 added totals 15 and counts 3 through its own generic, that the empty measurement counts 0 and totals 0 ms, and that modifying a copy to 9 leaves the original 3 in place. They do not test what happens when someone bypasses the constructor and never calls the validator.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
