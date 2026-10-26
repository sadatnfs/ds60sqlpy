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

**Expected evidence:** The values are 6,12,18.

### Exercise 2

Use fees c(1,2,3) for three amounts.

Adding to 10,20,30 gives 11,22,33.

**Expected evidence:** Adding to 10,20,30 gives 11,22,33.

### Exercise 3

Write a guard allowing one fee or one fee per amount.

length(fee) must be one or length(amount).

**Expected evidence:** length(fee) must be one or length(amount).

### Exercise 4

Diagnose two fees applied to four unrelated records.

Silent recycling can assign the wrong per-record fee.

**Expected evidence:** Silent recycling can assign the wrong per-record fee.

### Exercise 5

Inspect numeric(0) + 2.

It remains a numeric vector of length zero.

**Expected evidence:** It remains a numeric vector of length zero.

### Exercise 6

Keep an ID and a numeric measurement without coercing the measurement.

Use separate vectors or a list/data frame with explicit column types.

**Expected evidence:** Use separate vectors or a list/data frame with explicit column types.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
