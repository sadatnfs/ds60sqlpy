# r-007: reference reasoning

Use the [complete reference](r-007_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The updated binding has a different vector value. The original labels and values remain intact.

Both names point to the same environment. This is a reference object, so the mutation is visible through either binding.

## Explained practice

### Exercise 1

Predict x after y <- x; y[1] <- 9 for a numeric vector.

x retains its earlier first value.

**Expected evidence:** x retains its earlier first value.

### Exercise 2

Remove names from a labeled vector.

The values remain while names become NULL.

**Expected evidence:** The values remain while names become NULL.

### Exercise 3

Construct a two-column shape from four numbers.

A 2 by 2 matrix retains four values.

**Expected evidence:** A 2 by 2 matrix retains four values.

### Exercise 4

Diagnose a shared environment counter changing through another name.

Use a fresh environment when independent state is required.

**Expected evidence:** Use a fresh environment when independent state is required.

### Exercise 5

Test exact equality of c(A=1) and 1.

identical is FALSE because one object is named.

**Expected evidence:** identical is FALSE because one object is named.

### Exercise 6

State a function return contract including metadata.

Specify and test names, dimensions and class that downstream code relies on.

**Expected evidence:** Specify and test names, dimensions and class that downstream code relies on.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
