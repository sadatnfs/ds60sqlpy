# r-012: reference reasoning

Use the [complete reference](r-012_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The default and explicit-rate calls share one declared policy. The amount vector is allowed to vary in length, while the rate is scalar.

The result is a structured object, so downstream code can use its fields without parsing console text.

## Explained practice

### Exercise 1

Predict a ten-percent fee on 50.

The result is 45.

**Approach:** Call `after_fee(50)` and let the default rate of 0.1 apply.

**Why it holds here:** Omitting rate uses 0.1, so the function keeps 90 percent of the amount: 50 times 0.9 is 45.

**Tempting mistake:** Computing `50 * 0.1`, which is 5. That is the fee itself, not the amount after the fee, and it is off by a factor of nine.

**Verify:** `after_fee(50)` returns 45, matching the reference check.

### Exercise 2

Override the rate with zero.

The amount is unchanged.

**Approach:** Pass the rate by name: `after_fee(50, rate = 0)`.

**Why it holds here:** The explicit value replaces the default, and 0 passes the range check because the interface allows 0 through 1. Nothing is deducted, so 50 comes back.

**Tempting mistake:** Calling `after_fee(0, 50)` with the values in the wrong positions. Amount becomes 0 and rate becomes 50, which the range check rejects, so the caller gets an error rather than the unchanged amount.

**Verify:** `after_fee(50, rate = 0)` returns 50.

### Exercise 3

Write a function returning count and total.

The caller can inspect count and total separately.

**Approach:** Return `list(count = length(x), total = sum(x))` and let the caller read the fields.

**Why it holds here:** For c(2, 4) the count is 2 and the total is 6. length returns an integer, so the expected object is `list(count = 2L, total = 6)`.

**Tempting mistake:** Printing with `cat()` inside the function. The caller sees text on the console, but the function returns NULL, so `result$count` is NULL and cannot be tested.

**Verify:** `identical(summary(c(2, 4)), list(count = 2L, total = 6))` returns TRUE.

### Exercise 4

Diagnose a two-element rate for a scalar-rate interface.

Reject it before computing.

**Approach:** Include `length(rate) != 1L` in the validation so a vector rate stops before any arithmetic runs.

**Why it holds here:** With amount 50 and rate c(0.1, 0.2), arithmetic would recycle the amount and return 45 and 40, two answers to a one-policy question.

**Tempting mistake:** Relying on R to warn. Lengths 1 and 2 divide evenly, so recycling produces no warning, and Example 3 shows that two amounts with two rates are silent too.

**Verify:** In the reference `bad` returns TRUE, which only happens when the error handler ran.

### Exercise 5

Test an empty amount vector.

The vector fee function returns numeric(0); a summary can return count 0, total 0.

**Approach:** Pass `numeric(0)` and let vectorized arithmetic return an empty result.

**Why it holds here:** `numeric(0)` is numeric, so validation passes, and multiplying it by 0.9 gives numeric(0). The summary function gives count 0 and total 0 because `sum(numeric(0))` is 0.

**Tempting mistake:** Adding a check that the amount has at least one element. An empty batch is a normal input here, and rejecting it turns a quiet day into a failure.

**Verify:** `identical(after_fee(numeric(0)), numeric(0))` returns TRUE.

### Exercise 6

Explain a default-rate change during maintenance.

Treat the change as an interface change and test existing default callers.

**Approach:** Treat a new default as an interface change: find callers that omit rate and keep a test that pins `after_fee(50) == 45`.

**Why it holds here:** The reference shows `after_fee(50, rate = 0.2)` and `after_fee(50)` differ, 40 against 45. Every omitted-rate call would move if the default became 0.2.

**Tempting mistake:** Rerunning only tests that pass rate explicitly. They never exercise the default, so all of them stay green while every default caller changes.

**Verify:** The reference check `after_fee(50, rate = 0.2) != after_fee(50)` returns TRUE today; with a default of 0.2 it would return FALSE and stop.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
