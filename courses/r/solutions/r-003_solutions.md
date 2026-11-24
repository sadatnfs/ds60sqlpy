# r-003: reference reasoning

Use the [complete reference](r-003_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Length one is an intentional broadcast in this calculation. Each input receives the same fee.

No warning is needed because four is a multiple of two. The separate per-row length rule still rejects the input.

The reference defines a small checking helper with function(amount, fee). Its arguments receive the two input vectors, and its final logical expression reports whether the length rule holds. This avoids copying the guard for each boundary case. Chapter r-012 develops function interfaces in detail; the worked examples here can be followed with direct length checks.

## Explained practice

### Exercise 1

Predict c(2,4,6) * 3.

The values are 6,12,18.

**Approach:** Multiply the vector by the scalar and compare with the expected vector using `identical()`. The reference asserts `c(2, 4, 6) * 3` equals `c(6, 12, 18)`.

**Why it holds here:** A length-one multiplier is an intended broadcast: every element is multiplied by the same 3, so recycling is the contract rather than an accident.

**Tempting mistake:** Predicting a single number such as 36 by imagining that the vector is summed first. Arithmetic operators work element by element and return a vector of the same length as the longer operand.

**Verify:** `print(c(2, 4, 6) * 3)` shows `[1]  6 12 18`, three values, and `length()` of the result is 3.

### Exercise 2

Use fees c(1,2,3) for three amounts.

Adding to 10,20,30 gives 11,22,33.

**Approach:** Assert equal lengths, then add. The reference sets `fees <- c(1, 2, 3)`, checks `length(amount) == length(fees)` and expects 11, 22 and 33.

**Why it holds here:** With one fee per amount, each position pairs a record with its own fee, so 10 + 1, 20 + 2 and 30 + 3 are the intended row sums.

**Tempting mistake:** Leaving the starter's two fees in place. `c(10, 20, 30) + c(1, 2)` returns 11, 22, 31 with a warning, and the third record is charged the first record's fee.

**Verify:** `stopifnot(identical(amount + fees, c(11, 22, 33)))` passes, and no warning is printed during the run.

### Exercise 3

Write a guard allowing one fee or one fee per amount.

length(fee) must be one or length(amount).

**Approach:** Write a small predicate that accepts a fee of length one or a fee whose length equals the amounts. The reference's `valid()` helper returns that logical.

**Why it holds here:** The two allowed shapes are exactly the two intended contracts in this lesson: a flat fee for everyone or one fee per record. Every other length is rejected before arithmetic runs.

**Tempting mistake:** Accepting any length that divides evenly, using a remainder test such as `length(amount) %% length(fee) == 0`. That passes two fees for four records, the silent pattern from Example 2.

**Verify:** The reference checks `valid(amount, 2)` and `valid(amount, fees)` are TRUE and `valid(amount, c(1, 2))` is FALSE for three amounts.

### Exercise 4

Diagnose two fees applied to four unrelated records.

Silent recycling can assign the wrong per-record fee.

**Approach:** Compare the lengths and ask whether a two-element pattern has any meaning for the four records. Divisibility only explains why R stayed quiet.

**Why it holds here:** Example 2 returns 11, 22, 31 and 42 with no warning, yet nothing says records three and four should reuse the first two fees.

**Tempting mistake:** Concluding that the result is valid because no warning appeared. The lack of a warning is a property of the lengths four and two, not evidence that the fee schedule repeats.

**Verify:** Apply the per-row rule: `length(amount) == length(fees)` is FALSE for these inputs, which is the check Example 2 asserts with `stopifnot(!valid_per_row)`.

### Exercise 5

Inspect numeric(0) + 2.

It remains a numeric vector of length zero.

**Approach:** Evaluate `numeric(0) + 2` and inspect its length and type rather than its printed form.

**Why it holds here:** Recycling to the longer length does not apply when one operand is empty: the result has length zero, so there is nothing to add the fee to and nothing is invented.

**Tempting mistake:** Expecting the scalar 2, or an NA, as if an empty vector were a zero or a missing amount. Code that then takes `result[[1]]` fails with a subscript out of bounds error.

**Verify:** The reference asserts `length(numeric(0) + 2) == 0L`; `print()` shows `numeric(0)` and `typeof()` is still "double".

### Exercise 6

Keep an ID and a numeric measurement without coercing the measurement.

Use separate vectors or a list/data frame with explicit column types.

**Approach:** Keep the identifier and the measurement in separate vectors, or later in a data frame with explicit column types, instead of one atomic vector.

**Why it holds here:** `c("A", 2)` forces a common type and turns 2 into the text "2", so the measurement can no longer be added or compared numerically. The reference asserts `is.character(c("A", 2))` to show the coercion.

**Tempting mistake:** Calling `as.numeric()` on the combined vector to rescue the number. That produces NA for "A" with a coercion warning, so one value is lost to fix the other.

**Verify:** `is.double(c(1, 2))` returns TRUE for the separate measurement vector, and `c("A", 2)[2] + 1` fails with a non-numeric argument error.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
