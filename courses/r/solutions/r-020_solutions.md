# r-020: reference reasoning

Use the [complete reference](r-020_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The independent expected amount is (10+60)/4. Scaling every weight by the same positive constant is a useful invariant that tests meaning rather than source text.

Resetting the same seed before each draw reproduces this generator stream in the same environment. The range assertion checks a separate distribution-support property.

## Explained practice

### Exercise 1

Derive the weighted mean of 10 and 20 with weights 1 and 3.

The result is 17.5.

**Approach:** Derive the answer by hand first: the numerator is 10 times 1 plus 20 times 3, which is 70, and the denominator is the total weight 4, so the expected value is 17.5.

**Why it holds here:** A weight of 3 on 20 means 20 counts three times, so the result equals the plain mean of 10, 20, 20 and 20. Every intermediate value is an integer and 17.5 is exact in binary, so exact equality is safe for this fixture.

**Tempting mistake:** Dividing by the number of values, `sum(x * w) / length(x)`. That returns 35, which is larger than both inputs and cannot be a weighted average of them.

**Verify:** `weighted_average(c(10, 20), c(1, 3))` returns 17.5, matching the hand-derived 70 divided by 4.

### Exercise 2

Multiply every weight by five.

The weighted mean stays 17.5.

**Approach:** Call the function with the weights 5 and 15 and compare the result with the unscaled call.

**Why it holds here:** Multiplying every weight by five multiplies the numerator to 350 and the denominator to 20, and the ratio is still 17.5. The test checks a property of weighted means rather than restating the formula, so it catches implementations that merely look right.

**Tempting mistake:** Testing only the original weights. The division-by-count bug returns 35 for weights 1 and 3 but 175 for 5 and 15; the scaling test exposes it because a correct result cannot change with scale.

**Verify:** `weighted_average(c(10, 20), c(5, 15))` returns 17.5, the same value as the unscaled call.

### Exercise 3

Add tests for mismatched lengths and zero total weight.

Both should be rejected explicitly.

**Approach:** Call the function through a narrow `tryCatch(..., error = function(e) TRUE)` helper for weights `1` and for weights `c(0, 0)`, and require TRUE for both.

**Why it holds here:** These break different parts of the contract. A single weight would otherwise be recycled across both values, and two zero weights would divide 0 by 0, so each needs its own stopifnot condition and its own test.

**Tempting mistake:** Assuming R stops on its own. Without the checks the length mismatch silently returns 30, because the weight 1 is reused for 20, and the zero weights return NaN instead of an error.

**Verify:** `rejected(c(10, 20), 1)` and `rejected(c(10, 20), c(0, 0))` both return TRUE.

### Exercise 4

Diagnose a test comparing a function with the same copied formula.

Add independently derived fixtures and invariants.

**Approach:** Replace the copied formula in the test with hand-derived constants and with invariants whose answers are known without running the function.

**Why it holds here:** If the function divided by `length(w)` and the test computed its expected value with the same line, both sides would return 35 and the test would pass. 17.5 comes from arithmetic done separately, and the special cases below have obvious answers.

**Tempting mistake:** Writing `expected <- sum(x * w) / length(w)` in the test. Any mistake in the function is copied into the expectation, so the test can never fail for that mistake.

**Verify:** `weighted_average(c(10, 20), c(0, 1))` returns 20, and `weighted_average(c(10, 20), c(1, 1))` returns 15, the plain mean.

### Exercise 5

Repeat a random draw under the same seed.

The vectors match within the declared environment/generator configuration.

**Approach:** Call `set.seed(17)` immediately before each `runif(4)` and compare the two vectors with `identical()`.

**Why it holds here:** Resetting the seed puts the generator back in the same state, so both draws read the same four numbers in this R version with this generator. The range check is a separate property that holds for any seed.

**Tempting mistake:** Setting the seed once and then drawing twice. The second call continues the stream, so the vectors differ. Comparing across R versions can also fail: R 3.6.0 changed how sample() uses the stream.

**Verify:** `identical(first, second)` returns TRUE, and `RNGkind()` shows the generator names to record with the result.

### Exercise 6

Write a useful bug report for a dropped matrix dimension.

A reviewer can reproduce the failure without the original private data or hidden session.

**Approach:** Write the report with a synthetic input, the exact call, the observed shape, the expected shape, the fix and the R version, as in the guide section.

**Why it holds here:** The dimension is dropped whenever one row is selected, so a 2 by 3 matrix built from 1:6 reproduces the failure without the private data. Shapes give the reviewer a check they can run in seconds.

**Tempting mistake:** Reporting that the summary broke and attaching the full data. The reviewer cannot share or run it, and nothing says which call changed the shape.

**Verify:** `dim(m[1, ])` returns NULL, while `dim(m[1, , drop = FALSE])` returns 1 3 in a fresh session.

## What the checks establish

The reference makes 7 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
