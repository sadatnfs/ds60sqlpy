# r-015: reference reasoning

Use the [complete reference](r-015_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The rejected input remains distinguishable from a valid count of zero. Its diagnostic is retained for the caller.

The calling handler records this known warning and permits the expression to finish. The retained warning remains evidence alongside the value.

## Explained practice

### Exercise 1

Distinguish a valid zero from a rejected count.

Both cannot be represented by the same unexplained numeric zero.

**Expected evidence:** Both cannot be represented by the same unexplained numeric zero.

### Exercise 2

Add a valid digit-only input "0".

The result is successful with value 0.

**Expected evidence:** The result is successful with value 0.

### Exercise 3

Return structured status, value and diagnostic fields.

Callers can aggregate rejection rates without parsing arbitrary console output.

**Expected evidence:** Callers can aggregate rejection rates without parsing arbitrary console output.

### Exercise 4

Diagnose tryCatch(..., error=function(e)0) around a whole pipeline.

Catch only expected failures at a narrow boundary and retain diagnostics.

**Expected evidence:** Catch only expected failures at a narrow boundary and retain diagnostics.

### Exercise 5

Restore a changed option after an error.

on.exit restores the original option when the function exits.

**Expected evidence:** on.exit restores the original option when the function exits.

### Exercise 6

Explain when suppressing a warning is justified.

Handle or record a specifically understood warning; do not silence all new warnings by default.

**Expected evidence:** Handle or record a specifically understood warning; do not silence all new warnings by default.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
