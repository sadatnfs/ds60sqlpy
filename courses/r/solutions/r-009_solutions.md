# r-009: reference reasoning

Use the [complete reference](r-009_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The one-element list and the numeric measurement vector are different objects. Exact nested names retain the unit contract.

Single-bracket replacement retains the field with a NULL value; dollar replacement by NULL deletes the field.

## Explained practice

### Exercise 1

Predict is.list(x[1]) for a list x.

It is TRUE.

**Expected evidence:** It is TRUE.

### Exercise 2

Extract the first number from a values field.

Use record[["values"]][[1]].

**Expected evidence:** Use record[["values"]][[1]].

### Exercise 3

Validate required id and values fields.

Require both names, one character ID and a numeric values vector.

**Expected evidence:** Require both names, one character ID and a numeric values vector.

### Exercise 4

Diagnose an accidental one-element list passed to mean.

Use [[ to obtain the numeric field.

**Expected evidence:** Use [[ to obtain the numeric field.

### Exercise 5

Retain an explicitly NULL note field.

Use record["note"] <- list(NULL).

**Expected evidence:** Use record["note"] <- list(NULL).

### Exercise 6

Explain a risk of unlist on a mixed record.

A text ID can coerce numeric measurements to character and erase field structure.

**Expected evidence:** A text ID can coerce numeric measurements to character and erase field structure.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
