# r-011: reference reasoning

Use the [complete reference](r-011_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The output length is established before iteration. seq_along also gives the intended zero iterations for empty input.

Each iteration reduces the state and increments a bound. The final condition is checked separately from the iteration count.

## Explained practice

### Exercise 1

Predict squares for c(1,3).

The output is 1,9.

**Expected evidence:** The output is 1,9.

### Exercise 2

Use an empty input with seq_along.

No iterations occur and the output is numeric(0).

**Expected evidence:** No iterations occur and the output is numeric(0).

### Exercise 3

Construct a loop summing only positive values.

For -2,3,4 the total is seven.

**Expected evidence:** For -2,3,4 the total is seven.

### Exercise 4

Diagnose 1:length(x) on empty x.

It produces 1,0 rather than no indices.

**Expected evidence:** It produces 1,0 rather than no indices.

### Exercise 5

Bound a while loop that may not converge.

A maximum iteration count prevents unbounded work but is not convergence evidence.

**Expected evidence:** A maximum iteration count prevents unbounded work but is not convergence evidence.

### Exercise 6

Compare a clear loop with a vectorized equivalent.

Equivalent ordinary cases do not remove the need to test missingness and boundary policies.

**Expected evidence:** Equivalent ordinary cases do not remove the need to test missingness and boundary policies.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
