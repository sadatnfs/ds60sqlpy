# r-010: reference reasoning

Use the [complete reference](r-010_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The row permutation is applied to the entire data frame. Each ID retains its original amount.

The complete mask excludes the unknown amount. drop=FALSE preserves a table even though only one row and one column remain.

## Explained practice

### Exercise 1

Count rows and columns in a three-record two-field table.

nrow is three and ncol is two.

**Expected evidence:** nrow is three and ncol is two.

### Exercise 2

Add a derived amount_with_fee column.

Each row retains its ID and gains amount plus the declared fee.

**Expected evidence:** Each row retains its ID and gains amount plus the declared fee.

### Exercise 3

Validate a nonmissing unique ID column.

Use !anyNA(id) and !anyDuplicated(id).

**Expected evidence:** Use !anyNA(id) and !anyDuplicated(id).

### Exercise 4

Diagnose sorting only the amount column in place.

Sort entire rows with an order index.

**Expected evidence:** Sort entire rows with an order index.

### Exercise 5

Select zero rows while preserving columns and types.

The result has zero rows and the original schema.

**Expected evidence:** The result has zero rows and the original schema.

### Exercise 6

Distinguish repeated order IDs from duplicate line IDs.

A multi-line order can repeat OrderID while each LineID must remain unique.

**Expected evidence:** A multi-line order can repeat OrderID while each LineID must remain unique.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
