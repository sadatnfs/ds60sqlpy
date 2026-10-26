# r-032: reference reasoning

Use the [complete reference](r-032_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The observation mean counts four measurements equally. The equal-group mean gives A and B equal influence despite their unequal sizes.

The declared C category remains visible with zero rows and no observed mean. A missing measurement within A is separately counted.

## Explained practice

### Exercise 1

Reconstruct an overall mean from sums 10,90 and counts 1,3.

The mean is 25.

**Expected evidence:** The mean is 25.

### Exercise 2

Add another observation 50 to B.

Overall sum 150, count 5, mean 30.

**Expected evidence:** Overall sum 150, count 5, mean 30.

### Exercise 3

Return rows, observed, missing, sum and mean per group.

An all-missing group has observed 0 and an explicitly missing mean.

**Expected evidence:** An all-missing group has observed 0 and an explicitly missing mean.

### Exercise 4

Diagnose summing distinct-customer counts across overlapping groups.

Deduplicate the intended union or preserve an exact mergeable set/sketch contract.

**Expected evidence:** Deduplicate the intended union or preserve an exact mergeable set/sketch contract.

### Exercise 5

Retain a category with no observations.

Report zero rows separately from all-missing measured rows.

**Expected evidence:** Report zero rows separately from all-missing measured rows.

### Exercise 6

Explain why group medians cannot be averaged into an overall median.

Retain the necessary distribution state or recompute from admitted observations.

**Expected evidence:** Retain the necessary distribution state or recompute from admitted observations.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
