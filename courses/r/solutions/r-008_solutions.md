# r-008: reference reasoning

Use the [complete reference](r-008_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Each row combines an intercept and one feature with the same coefficient vector. Matrix multiplication preserves one output per observation.

The residual checks the solved equation. The extraction comparison shows why a one-column matrix needs an explicit shape policy.

## Explained practice

### Exercise 1

Predict the first row of matrix(1:6, nrow=2).

The first row is 1,3,5.

**Expected evidence:** The first row is 1,3,5.

### Exercise 2

Construct the same dimensions with byrow=TRUE.

The first row becomes 1,2,3.

**Expected evidence:** The first row becomes 1,2,3.

### Exercise 3

Compute predictions for intercept two and slope three at x=3,4.

The predictions are 11 and 14.

**Expected evidence:** The predictions are 11 and 14.

### Exercise 4

Diagnose replacing %*% with *.

Keep the matrix product and validate dimensions.

**Expected evidence:** Keep the matrix product and validate dimensions.

### Exercise 5

Retain one selected column as a matrix.

Use drop=FALSE and test dim.

**Expected evidence:** Use drop=FALSE and test dim.

### Exercise 6

Explain why a residual check is useful after solve.

A small residual supports this numerical solution but does not by itself establish good conditioning or correct model assumptions.

**Expected evidence:** A small residual supports this numerical solution but does not by itself establish good conditioning or correct model assumptions.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
