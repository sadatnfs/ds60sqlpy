# r-014: reference reasoning

Use the [complete reference](r-014_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The prototype states that every group produces one numeric total. Group names remain available for interpretation.

A list is appropriate for structured group outputs. The pipe is ordinary sequential evaluation with an inspectable intermediate order.

## Explained practice

### Exercise 1

Predict vapply(list(c(1,2), c(3)), sum, numeric(1)).

The result is 3,3.

**Expected evidence:** The result is 3,3.

### Exercise 2

Add an empty group to a sum mapping.

The new group total is zero, under that declared policy.

**Expected evidence:** The new group total is zero, under that declared policy.

### Exercise 3

Map count and mean into a list per group.

Use lapply and explicitly handle all-missing or empty means.

**Expected evidence:** Use lapply and explicitly handle all-missing or empty means.

### Exercise 4

Diagnose a mapped function returning two numbers under numeric(1).

vapply raises an incompatibility instead of changing shape silently.

**Expected evidence:** vapply raises an incompatibility instead of changing shape silently.

### Exercise 5

Map an empty collection.

vapply with numeric(1) returns an empty numeric result.

**Expected evidence:** vapply with numeric(1) returns an empty numeric result.

### Exercise 6

Explain why a pipe does not accelerate a computation automatically.

Measure an actual equivalent workload before making a performance claim.

**Expected evidence:** Measure an actual equivalent workload before making a performance claim.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
