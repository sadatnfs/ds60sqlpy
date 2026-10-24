# csharp-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-008_solution.cs](csharp-008_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Copy the storage deliberately:** Primitive elements are values, so cloning this array provides independent element storage. The alias changes source; the copied integer array retains 2.

**Respect distinct dimensions:** Different dimension sizes expose swapped-boundary mistakes that a square fixture can hide. The shape is two by three and the sum is 21.

## Reason through the six tasks

1. **Predict and explain.** Predict source and copy after alias mutation.

2. **Guided modification.** Change only the copied array and verify source is unchanged.

3. **Independent construction.** Compute each row sum of the two-by-three grid.

4. **Diagnose a defect.** Diagnose a nested loop that uses the row count for both dimensions.

5. **Boundary evidence.** Test an empty array and a one-row rectangular array.

6. **Transfer and justify.** Choose rectangular or jagged storage for variable-length sensor histories and justify the choice.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An array has a fixed number of elements with one element type. Its length does not grow after creation. Assignment copies the array reference, so two variables can refer to the same storage. A copied array can separate the outer storage while still sharing referenced elements. Before using a copy, identify which level of independence the algorithm needs.

A rectangular array has dimensions built into its shape; a jagged array is an array of arrays whose row lengths may differ. Data-science work often fails at shape boundaries before the numerical formula is wrong. Make row and column assumptions explicit and test a non-square fixture so swapping dimensions cannot accidentally pass.

`new int[3]` creates three zero-initialized entries. `values[0]` addresses the first. `int[,] grid` has rank two and GetLength selects a dimension. `int[][]` contains separate row arrays.

Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
