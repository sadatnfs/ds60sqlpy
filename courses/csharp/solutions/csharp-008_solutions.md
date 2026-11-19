# csharp-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-008_solution.cs](csharp-008_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Copy the storage deliberately:** Primitive elements are values, so cloning this array provides independent element storage. The alias changes source; the copied integer array retains 2.

**Respect distinct dimensions:** Different dimension sizes expose swapped-boundary mistakes that a square fixture can hide. The shape is two by three and the sum is 21.

## Task answers

### Task 1: Predict and explain

Predict source and copy after alias mutation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Primitive elements are values, so cloning this array provides independent element storage. The alias changes source; the copied integer array retains 2.

### Task 2: Guided modification

Change only the copied array and verify source is unchanged.

No separate reference answer has been written for this task. Start from Example B: Different dimension sizes expose swapped-boundary mistakes that a square fixture can hide. The shape is two by three and the sum is 21.

### Task 3: Independent construction

Compute each row sum of the two-by-three grid.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int[,] grid = { { 1, 2, 3 }, { 4, 5, 6 } };
int[] rowSums = new int[grid.GetLength(0)];
for (int row = 0; row < grid.GetLength(0); row++) {
  for (int col = 0; col < grid.GetLength(1); col++) {
    rowSums[row] += grid[row, col];
  }
}
Check(rowSums.SequenceEqual(new[] { 6, 15 }), "one sum per row");
```

**Observe:** The row sums are 6 and 15.

The outer loop owns one result slot per row, and GetLength keeps both bounds tied to the actual rectangle.

### Task 4: Diagnose a defect

Diagnose a nested loop that uses the row count for both dimensions.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.

### Task 5: Boundary evidence

Test an empty array and a one-row rectangular array.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Copy the storage deliberately) and Example B (Respect distinct dimensions).

### Task 6: Transfer and justify

Choose rectangular or jagged storage for variable-length sensor histories and justify the choice.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Array**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An array has a fixed number of elements with one element type. Its length does not grow after creation. Assignment copies the array reference, so two variables can refer to the same storage. A copied array can separate the outer storage while still sharing referenced elements. Before using a copy, identify which level of independence the algorithm needs.

A rectangular array has dimensions built into its shape; a jagged array is an array of arrays whose row lengths may differ. Data-science work often fails at shape boundaries before the numerical formula is wrong. Make row and column assumptions explicit and test a non-square fixture so swapping dimensions cannot accidentally pass.

`new int[3]` creates three zero-initialized entries. `values[0]` addresses the first. `int[,] grid` has rank two and GetLength selects a dimension. `int[][]` contains separate row arrays.

Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.

## Review before continuing

Run the reference and confirm that it prints `csharp-008: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
