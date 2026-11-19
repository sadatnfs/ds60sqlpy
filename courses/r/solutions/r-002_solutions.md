# r-002: reference reasoning

Use the [complete reference](r-002_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Numeric equality and exact object identity make different claims. The storage difference is intentional.

The decimal check allows a tiny representation error. Grouping uses exact small integer arithmetic and keeps quotient separate from remainder.

## Explained practice

### Exercise 1

Predict the storage type of c(1L, 2.5).

Both entries are stored as doubles.

### Exercise 2

Replace numeric 17 with the identifier "0017".

Keep the identifier character to preserve leading zeros.

### Exercise 3

Check that 19 items form three groups of five with four left.

19 %/% 5 is 3 and 19 %% 5 is 4.

### Exercise 4

Diagnose identical(2L, 2) being false.

The storage types differ even though numeric equality holds.

### Exercise 5

Check a decimal calculation near 0.3.

isTRUE(all.equal(...)) supplies one logical result.

### Exercise 6

State why a large tolerance can hide a defect.

A tolerance should permit representation error, not an arbitrary change in the intended amount.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
