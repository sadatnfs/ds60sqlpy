# r-012: reference reasoning

Use the [complete reference](r-012_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The default and explicit-rate calls share one declared policy. The amount vector is allowed to vary in length, while the rate is scalar.

The result is a structured object, so downstream code can use its fields without parsing console text.

## Explained practice

### Exercise 1

Predict a ten-percent fee on 50.

The result is 45.

**Expected evidence:** The result is 45.

### Exercise 2

Override the rate with zero.

The amount is unchanged.

**Expected evidence:** The amount is unchanged.

### Exercise 3

Write a function returning count and total.

The caller can inspect count and total separately.

**Expected evidence:** The caller can inspect count and total separately.

### Exercise 4

Diagnose a two-element rate for a scalar-rate interface.

Reject it before computing.

**Expected evidence:** Reject it before computing.

### Exercise 5

Test an empty amount vector.

The vector fee function returns numeric(0); a summary can return count 0, total 0.

**Expected evidence:** The vector fee function returns numeric(0); a summary can return count 0, total 0.

### Exercise 6

Explain a default-rate change during maintenance.

Treat the change as an interface change and test existing default callers.

**Expected evidence:** Treat the change as an interface change and test existing default callers.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
