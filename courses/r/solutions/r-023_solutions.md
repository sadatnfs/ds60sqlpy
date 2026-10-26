# r-023: reference reasoning

Use the [complete reference](r-023_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The alias test establishes reference identity directly with identical, then tests observable mutation. The scalar clone and nested box tests isolate two different depths of copying. Validation tests check that rejection happens before mutation, rather than merely checking that some error occurs.

Fresh counters within the fold function demonstrate one ownership policy for independent analytical tasks. The example makes no claim that default deep cloning duplicates every environment, file handle or external resource. Those need their own lifecycle and copying rules.

## Explained practice

### Exercise 1

Predict two readings after a=Counter$new(2), b=a and b$add(3).

Both names refer to one counter and read 5.

**Expected evidence:** Both readings 5.

### Exercise 2

Make a separate scalar counter with clone and add four.

The clone reads 9 while the original remains 5.

**Expected evidence:** Original 5, clone 9.

### Exercise 3

Verify that a rejected negative increment leaves the counter unchanged.

add(-1) fails and both readings remain equal.

**Expected evidence:** Validation error and unchanged state.

### Exercise 4

Construct a box containing a Counter and compare shallow and deep copies.

The shallow copy shares its nested counter with the original; deep=TRUE clones that R6 member.

**Expected evidence:** Three readings demonstrate the stated identities.

### Exercise 5

Diagnose using one mutable counter for every resampling fold.

Construct a fresh counter per fold or define and test a reset policy. Reassignment alone does not isolate it.

**Expected evidence:** No cross-fold state leakage.

### Exercise 6

State the limit of clone(deep=TRUE) for an arbitrary environment member.

Default deep cloning does not promise a full snapshot of arbitrary environments or connections. Design and test a custom deep_clone policy if such resources are allowed.

**Expected evidence:** A bounded cloning claim.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
