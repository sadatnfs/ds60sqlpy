# r-023: reference reasoning

Run the [complete reference](r-023_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The alias test establishes reference identity directly with identical, then tests observable mutation. The scalar clone and nested box tests isolate two different depths of copying. Validation tests check that rejection happens before mutation, rather than merely checking that some error occurs.

Fresh counters within the fold function demonstrate one ownership policy for independent analytical tasks. The example makes no claim that default deep cloning duplicates every environment, file handle or external resource. Those need their own lifecycle and copying rules.

## Explained practice

### Exercise 1

Predict two readings after a=Counter$new(2), b=a and b$add(3).

Both names refer to one counter and read 5.

**Expected evidence:** Both readings 5.

**Approach:** Track objects rather than names: `Counter$new(2)` creates one object, `b <- a` binds a second name to it, and `b$add(3)` changes the private value of that single object.

**Why it holds here:** An R6 object is an environment, and assigning an environment copies only the reference. Both names therefore lead to the same private value, which goes from 2 to 5.

**Tempting mistake:** Reasoning as for a list and expecting a to stay at 2. That is how the r-021 measurement behaves, but there is no copy here for the change to land in.

**Verify:** `a$read()` and `b$read()` both return 5, and `identical(a, b)` returns TRUE.

### Exercise 2

Make a separate scalar counter with clone and add four.

The clone reads 9 while the original remains 5.

**Expected evidence:** Original 5, clone 9.

**Approach:** Call `copy <- a$clone()` first, then `copy$add(4)`.

**Why it holds here:** clone() creates a new object whose private value starts at the current 5. The addition touches only that new object, so it reads 9 and a still reads 5.

**Tempting mistake:** Writing `copy <- a` and then adding. Both names point at one counter, so both read 9 and the original value is lost.

**Verify:** `copy$read()` returns 9, and `a$read()` returns 5.

### Exercise 3

Verify that a rejected negative increment leaves the counter unchanged.

add(-1) fails and both readings remain equal.

**Expected evidence:** Validation error and unchanged state.

**Approach:** Record `before <- a$read()`, call `a$add(-1)` inside a handler that expects "nonnegative finite", then read again and compare.

**Why it holds here:** add() validates the amount before it assigns private$value, so the error stops the method before any change. NA_real_ fails the same is.finite test.

**Tempting mistake:** Updating first and validating afterward. The counter would already read 4 when the error is raised, leaving a half-applied change that the caller cannot see.

**Verify:** `a$read()` returns 5 after the failed call, the same value as `before`.

### Exercise 4

Construct a box containing a Counter and compare shallow and deep copies.

The shallow copy shares its nested counter with the original; deep=TRUE clones that R6 member.

**Expected evidence:** Three readings demonstrate the stated identities.

**Approach:** Clone the Box both ways, add 2 through the shallow copy and 5 through the deep copy, then read all three counters.

**Why it holds here:** A shallow clone copies the Box but its counter field still refers to the same Counter, so adding 2 changes the original too: 1 plus 2 is 3. With deep = TRUE, R6 clones fields that are R6 objects, so the deep counter goes from 1 to 6 alone.

**Tempting mistake:** Assuming clone() isolates nested objects and expecting the original to stay at 1.

**Verify:** `original$counter$read()` returns 3, `shallow$counter$read()` returns 3, and `deep$counter$read()` returns 6.

### Exercise 5

Diagnose using one mutable counter for every resampling fold.

Construct a fresh counter per fold or define and test a reset policy. Reassignment alone does not isolate it.

**Expected evidence:** No cross-fold state leakage.

**Approach:** Construct a new Counter inside the function applied to each fold, as the reference does in `vapply(c(2, 5, 1), ...)`.

**Why it holds here:** Each call creates its own counter starting at 0, so the readings are 2, 5 and 1, and the result for a fold does not depend on which folds ran before it.

**Tempting mistake:** Creating one counter outside the loop and adding each fold's amount to it. The readings become 2, 7 and 8, so later folds report inflated values and reordering the folds changes the results.

**Verify:** `fold_values` returns 2, 5, 1, and running the folds in reverse returns 1, 5, 2.

### Exercise 6

State the limit of clone(deep=TRUE) for an arbitrary environment member.

Default deep cloning does not promise a full snapshot of arbitrary environments or connections. Design and test a custom deep_clone policy if such resources are allowed.

**Expected evidence:** A bounded cloning claim.

**Approach:** Limit the claim: `clone(deep = TRUE)` deep copies fields that are R6 objects. For a plain environment or a connection, write a private deep_clone method that states what is copied, and test it.

**Why it holds here:** The Box test shows R6 fields being copied. R6's default deep copy leaves other environments shared, and a connection to a file cannot be duplicated at all.

**Tempting mistake:** Describing deep = TRUE as a full snapshot. A cache environment field would still be shared, and a change made through the clone would appear in the original.

**Verify:** For a class with a plain environment field env, `identical(obj$clone(deep = TRUE)$env, obj$env)` returns TRUE, showing that it is still shared.

## What the checks establish

The assertions confirm that a rejected increment raises the expected message, that `a` and `b` are the same object reading 5, that a clone advanced to 9 leaves `a` at 5, that a failed add leaves the state unchanged, that a shallow clone shares its inner counter while a deep clone advances separately to 6, and that per-fold counters produce 2, 5 and 1. They do not cover environments that are not R6 objects.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
