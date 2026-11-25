# r-002: reference reasoning

Run the [complete reference](r-002_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

Numeric equality and exact object identity make different claims. The storage difference is intentional.

The decimal check allows a tiny representation error. Grouping uses exact small integer arithmetic and keeps quotient separate from remainder.

## Explained practice

### Exercise 1

Predict the storage type of c(1L, 2.5).

Both entries are stored as doubles.

**Approach:** Combine the two values and inspect the result with `typeof()`. The reference asserts `typeof(c(1L, 2.5)) == "double"`.

**Why it holds here:** An atomic vector holds one type. 2.5 cannot be stored as an integer, so R promotes the integer 1L to double; the value 1 is unchanged, only its storage widens. Printing the vector shows `[1] 1.0 2.5` because both entries share one numeric format.

**Tempting mistake:** Predicting "integer" because the first element was written with the L suffix, or expecting each element to keep its own type. That would be true of a list, not of `c()`.

**Verify:** `typeof(c(1L, 2.5))` prints "double" and `is.integer(c(1L, 2.5))` is FALSE.

### Exercise 2

Replace numeric 17 with the identifier "0017".

Keep the identifier character to preserve leading zeros.

**Approach:** Keep the starter's identifier as the character string "0017". The reference asserts `is.character(identifier)` and `nchar(identifier) == 4`.

**Why it holds here:** An identifier labels a record; nobody adds or averages identifiers, and its leading zeros are part of the label. Character storage preserves all four characters exactly as written.

**Tempting mistake:** Converting with `as.numeric("0017")` yields 17, and `as.character()` on that gives "17", only two characters. Two different codes such as "017" and "0017" would also collapse into the same number 17.

**Verify:** `print(identifier)` shows "0017" with quotes, and `nchar(identifier)` returns 4. Running `nchar(as.character(as.numeric(identifier)))` returns 2, which shows the loss.

### Exercise 3

Check that 19 items form three groups of five with four left.

19 %/% 5 is 3 and 19 %% 5 is 4.

**Approach:** Compute the number of full groups with `19 %/% 5` and the leftover items with `19 %% 5` as two separate results. The reference asserts 3 and 4.

**Why it holds here:** The starter supplies 19 items and a group size of 5. Three groups use 15 items and 4 remain, and 3 * 5 + 4 rebuilds 19, so the pair accounts for every item.

**Tempting mistake:** Using `round(19 / 5)` gives 4, claiming a fourth full group that would need 20 items. Using `ceiling()` answers a different question, the number of boxes needed, which may be valid elsewhere but is not this task.

**Verify:** `stopifnot(19 %/% 5 * 5 + 19 %% 5 == 19)` passes, and printing both results shows 3 and 4.

### Exercise 4

Diagnose identical(2L, 2) being false.

The storage types differ even though numeric equality holds.

**Approach:** Inspect each side with `typeof()` and compare the two kinds of test: `2L == 2` asks about value after coercion, while `identical(2L, 2)` also compares storage type.

**Why it holds here:** 2L is an integer and 2 is a double, so identity fails even though numeric equality holds. The reference asserts both `!identical(2L, 2)` and `2L == 2` to keep the two claims separate.

**Tempting mistake:** Concluding that 2L and 2 are different numbers, or writing `identical(length(x), 3)` as a test. `length()` returns an integer, so that check is FALSE for a three-element vector; `identical(length(x), 3L)` is the matching form.

**Verify:** `typeof(2L)` prints "integer", `typeof(2)` prints "double", and `2L == 2` prints TRUE.

### Exercise 5

Check a decimal calculation near 0.3.

isTRUE(all.equal(...)) supplies one logical result.

**Approach:** Wrap the comparison as `isTRUE(all.equal(0.1 + 0.2, 0.3, tolerance = 1e-12))` so the check produces one logical value.

**Why it holds here:** The representation error here is about 5.55e-17, many orders of magnitude below 1e-12, so the tolerance accepts rounding noise while still rejecting a real change in amount.

**Tempting mistake:** Writing `0.1 + 0.2 == 0.3` gives FALSE. Using `all.equal()` alone inside `if` or `stopifnot` is also risky: when values differ it returns a text description such as a mean relative difference, not FALSE, so the condition is not a clean logical.

**Verify:** The reference also asserts `!isTRUE(all.equal(0.31, 0.3, tolerance = 1e-12))`, so the check still rejects a 0.01 change.

### Exercise 6

State why a large tolerance can hide a defect.

A tolerance should permit representation error, not an arbitrary change in the intended amount.

**Approach:** Choose the tolerance from the units and the decision, then test that it rejects a defect you care about. Here 1e-12 covers double rounding for values near 0.3.

**Why it holds here:** all.equal measures relative difference. For 0.31 against 0.3 that is about 0.03, so 1e-12 correctly rejects it, which is the second check in the reference.

**Tempting mistake:** Setting `tolerance = 0.1` so a stubborn check passes. `all.equal(0.31, 0.3, tolerance = 0.1)` returns TRUE, silently accepting a 3 percent error in an amount that should have been exact to the cent.

**Verify:** Run both tolerances on 0.31 versus 0.3: 1e-12 gives a difference message, while 0.1 gives TRUE. That contrast is the evidence that a loose tolerance can hide a defect.

## What the checks establish

The assertions confirm that combining `1L` with 2.5 yields a double, that `"0017"` keeps four characters, that `19 %/% 5` is 3 with 4 left over, that `2L == 2` holds while `identical(2L, 2)` does not, and that `all.equal()` accepts 0.1 + 0.2 as 0.3 but rejects 0.31. They do not choose a tolerance for your own measurements; that remains a decision about the data.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
