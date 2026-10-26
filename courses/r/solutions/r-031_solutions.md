# r-031: reference reasoning

Use the [complete reference](r-031_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The missing quantity is excluded explicitly. The final row permutation preserves ID/amount alignment and makes the result deterministic.

The total is seven plus thirteen regardless of input row order. This invariant would not apply unchanged to a sequence-dependent lag calculation.

## Explained practice

### Exercise 1

Trace the two retained rows in the first example.

L1 has 8 and L3 has 9; L2 has an unknown amount.

**Expected evidence:** L1 has 8 and L3 has 9; L2 has an unknown amount.

### Exercise 2

Raise the threshold from eight to nine.

L3 remains with net 9.

**Expected evidence:** L3 remains with net 9.

### Exercise 3

Return an exclusion count alongside the selected table.

Report input 3, retained 2, excluded 1 under the original policy.

**Expected evidence:** Report input 3, retained 2, excluded 1 under the original policy.

### Exercise 4

Diagnose sorting only prices before multiplication.

Permute complete rows or join by a validated key.

**Expected evidence:** Permute complete rows or join by a validated key.

### Exercise 5

Handle an input with no qualifying rows.

Return a zero-row id/net data frame with declared types.

**Expected evidence:** Return a zero-row id/net data frame with declared types.

### Exercise 6

Transfer the pipeline to a lagged feature.

Sort by entity, time and a deterministic tie-breaker before computing lags.

**Expected evidence:** Sort by entity, time and a deterministic tie-breaker before computing lags.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
