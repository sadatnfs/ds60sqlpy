# r-014: reference reasoning

Run the [complete reference](r-014_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The prototype states that every group produces one numeric total. Group names remain available for interpretation.

A list is appropriate for structured group outputs. The pipe is ordinary sequential evaluation with an inspectable intermediate order.

## Explained practice

### Exercise 1

Predict vapply(list(c(1,2), c(3)), sum, numeric(1)).

The result is 3,3.

**Approach:** Map `sum` over the two elements with vapply and a `numeric(1)` prototype.

**Why it holds here:** The first element sums to 3 and the second is already 3, so the result is the unnamed vector 3, 3; the input list has no names to carry over.

**Tempting mistake:** Calling `sum(unlist(...))`. That returns 6, one grand total, and loses the per-group structure the task asks for.

**Verify:** `identical(vapply(list(c(1, 2), c(3)), sum, numeric(1)), c(3, 3))` returns TRUE.

### Exercise 2

Add an empty group to a sum mapping.

The new group total is zero, under that declared policy.

**Approach:** Keep the empty group in the list and map `sum` as before.

**Why it holds here:** `sum(numeric(0))` is 0, which fits the numeric(1) prototype, so the empty group gets total 0 under the documented convention.

**Tempting mistake:** Summarizing with `max`. For the empty group it returns -Inf with a warning, which fits the prototype too, so vapply accepts a value no report should show.

**Verify:** `vapply(groups, sum, numeric(1))[["empty"]]` returns 0.

### Exercise 3

Map count and mean into a list per group.

Use lapply and explicitly handle all-missing or empty means.

**Approach:** Use lapply with a function that returns `list(n = length(x), mean = ...)`, branching to NA_real_ when the group is empty.

**Why it holds here:** Each group needs two fields, so a list per group fits. A has mean 1.5, and the empty group gets n 0 with an explicit NA.

**Tempting mistake:** Calling `mean(x)` without the branch. The empty group gets NaN, which `is.na()` also accepts, so the check passes while the output suggests an arithmetic fault.

**Verify:** `summary$A$mean` returns 1.5 and `summary$empty$n` returns 0.

### Exercise 4

Diagnose a mapped function returning two numbers under numeric(1).

vapply raises an incompatibility instead of changing shape silently.

**Approach:** Run the two-value function under vapply with numeric(1) inside tryCatch and confirm that it stops.

**Why it holds here:** The prototype promises one number per element, and `c(x, x)` returns two, so vapply raises an error naming the length mismatch.

**Tempting mistake:** Switching to sapply to make the error go away. It returns a two-row matrix, so code that expects one value per group receives a different shape with no message.

**Verify:** In the reference `bad` returns TRUE because the error handler ran.

### Exercise 5

Map an empty collection.

vapply with numeric(1) returns an empty numeric result.

**Approach:** Map over `list()` with vapply and the same numeric(1) prototype.

**Why it holds here:** There are no elements to call, and the prototype still fixes the type, so the result is numeric(0).

**Tempting mistake:** Using sapply here. As Example 3 shows, it returns an empty list, which fails an `is.numeric()` check and breaks code that later adds totals.

**Verify:** `identical(vapply(list(), sum, numeric(1)), numeric(0))` returns TRUE.

### Exercise 6

Explain why a pipe does not accelerate a computation automatically.

Measure an actual equivalent workload before making a performance claim.

**Approach:** Show that the piped and nested forms are the same call, and time a realistic workload only if speed matters.

**Why it holds here:** `quote()` reveals that `c(3, 1, 2) |> sort()` becomes `sort(c(3, 1, 2))`, so both versions sort the same three numbers.

**Tempting mistake:** Timing each spelling once on three numbers and reporting the faster one. The difference is noise, and no algorithm changed.

**Verify:** `identical(c(3, 1, 2) |> sort() |> head(2), head(sort(c(3, 1, 2)), 2))` returns TRUE.

## What the checks establish

The checks pin `vapply()` returning a numeric vector of 3 and 3, the empty group summing to 0 by definition, a per-group summary where A has mean 1.5 and the empty group has an NA mean rather than NaN, a rejected template mismatch, an empty list mapping to `numeric(0)`, and a base pipe that sorts and keeps 1 and 2. They do not show how your summaries behave when a group holds NA values or a different type.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
