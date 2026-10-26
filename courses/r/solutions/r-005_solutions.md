# r-005: reference reasoning

Use the [complete reference](r-005_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The requested output order is C, A, A, and duplication is preserved. This is positional extraction, not a unique-key set operation.

The first output preserves an unknown selected position. The second explicitly restricts selection to known TRUE predicates.

The reference catches the deliberately invalid mixed index so the remaining assertions can still run. That error-handling helper is explained in r-015. The selection mechanism does not depend on knowing the handler yet: positive positions retain, negative positions exclude, and those policies cannot be mixed in the illustrated index.

## Explained practice

### Exercise 1

Predict x[c(2,2,1)] for x=c(4,8).

The result is 8,8,4.

**Expected evidence:** The result is 8,8,4.

### Exercise 2

Exclude the middle entry of c(2,4,6).

The result is 2,6.

**Expected evidence:** The result is 2,6.

### Exercise 3

Select and update a validated named value.

With unique names A, B, updating B changes only that entry.

**Expected evidence:** With unique names A, B, updating B changes only that entry.

### Exercise 4

Diagnose mixing c(1,-2) as an index.

Use one indexing policy, such as c(1,3) or -2.

**Expected evidence:** Use one indexing policy, such as c(1,3) or -2.

### Exercise 5

Inspect selection with integer(0).

The output length is zero.

**Expected evidence:** The output length is zero.

### Exercise 6

Explain why character names are not a validated join key.

Check uniqueness and missing names explicitly before keyed alignment.

**Expected evidence:** Check uniqueness and missing names explicitly before keyed alignment.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
