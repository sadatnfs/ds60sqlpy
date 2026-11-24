# r-011: reference reasoning

Use the [complete reference](r-011_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The output length is established before iteration. seq_along also gives the intended zero iterations for empty input.

Each iteration reduces the state and increments a bound. The final condition is checked separately from the iteration count.

## Explained practice

### Exercise 1

Predict squares for c(1,3).

The output is 1,9.

**Approach:** Trace the reference square function: i = 1 writes 1^2 into position 1, and i = 2 writes 3^2 into position 2 of the preallocated output.

**Why it holds here:** `numeric(length(x))` creates two slots, and each iteration fills exactly one, so the result is 1, 9.

**Tempting mistake:** Mixing preallocation with appending, as in `out <- c(out, x[[i]]^2)`. The two starting zeros stay in front and the result is 0, 0, 1, 9.

**Verify:** `square(c(1, 3))` returns c(1, 9) with length 2.

### Exercise 2

Use an empty input with seq_along.

No iterations occur and the output is numeric(0).

**Approach:** Call `square(numeric(0))` and let `seq_along` decide the iterations.

**Why it holds here:** An empty input has zero valid positions, so `seq_along` is integer(0), the body never runs, and the preallocated `numeric(0)` is returned unchanged.

**Tempting mistake:** Adding a guard that returns NULL for empty input. NULL is not numeric(0), so callers that check type or combine results get a different object than for any other input.

**Verify:** `identical(square(numeric(0)), numeric(0))` returns TRUE.

### Exercise 3

Construct a loop summing only positive values.

For -2,3,4 the total is seven.

**Approach:** Set `total <- 0` before the loop and add each value only when `value > 0`.

**Why it holds here:** -2 fails the test and is skipped, then 3 and 4 are added, so total goes 0, 3, 7 as the trace table shows.

**Tempting mistake:** Initializing total inside the loop. It resets on every pass, so after the last value total is 4, the contribution of a single element.

**Verify:** After the loop `total` returns 7, matching the reference check.

### Exercise 4

Diagnose 1:length(x) on empty x.

It produces 1,0 rather than no indices.

**Approach:** Evaluate `1:length(numeric(0))` on its own before running any loop that uses it.

**Why it holds here:** length is 0, and the colon operator counts down when the end is below the start, so 1:0 is the two indices 1 and 0.

**Tempting mistake:** Assuming 1:0 is an empty range. Example 3 shows the result: the loop runs twice and returns one NA from an input with no values.

**Verify:** `identical(1:0, c(1L, 0L))` returns TRUE, and `square_bad(numeric(0))` prints `[1] NA`.

### Exercise 5

Bound a while loop that may not converge.

A maximum iteration count prevents unbounded work but is not convergence evidence.

**Approach:** Combine the state test with a step bound in the condition, increment steps on each pass, and test the state again after the loop.

**Why it holds here:** Halving 20 gives 10, 5 and 2.5, so the state rule ends the loop after 3 passes, well inside the bound of 10.

**Tempting mistake:** Treating any exit as convergence. If the update never brought state below 3, the loop would stop at 10 steps and the code would still report success.

**Verify:** `steps` returns 3 and `state` is 2.5, and the separate `state <= 3` check shows which rule ended the loop.

### Exercise 6

Compare a clear loop with a vectorized equivalent.

Equivalent ordinary cases do not remove the need to test missingness and boundary policies.

**Approach:** Compare the loop with `x^2` using `identical()` on ordinary, empty and missing inputs.

**Why it holds here:** Both forms return doubles 1, 9 for c(1, 3), and `numeric(0)^2` is numeric(0), so identical holds in each case.

**Tempting mistake:** Comparing with `all(a == b)`. For c(1, NA) both forms give 1, NA, but `==` yields TRUE, NA and `all()` returns NA, so stopifnot fails on two equal results.

**Verify:** `identical(square(c(1, NA)), c(1, NA)^2)` returns TRUE.

## What the checks establish

The reference makes 4 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
