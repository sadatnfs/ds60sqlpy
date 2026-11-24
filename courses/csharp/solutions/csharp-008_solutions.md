# csharp-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-008_solution.cs](csharp-008_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Copy the storage deliberately:** Primitive elements are values, so cloning this array provides independent element storage. The alias changes source; the copied integer array retains 2.

**Respect distinct dimensions:** Different dimension sizes expose swapped-boundary mistakes that a square fixture can hide. The shape is two by three and the sum is 21.

## Task answers

### Task 1: Predict and explain

Predict source and copy after alias mutation.

**Written answer.** `alias` and `source` hold the same array reference, so `alias[0] = 9` writes into the one shared array and `source` becomes `{ 9, 4 }`. `copy` was cloned before the write into separate storage, so `copy[0]` is still 2.

**Why it is correct.** Arrays are reference types: assignment copies the reference, not the elements. `Clone` allocates a new `int[]` and copies each element, and `int` elements are values, so nothing is shared after the clone.

**Plausible wrong approach.** Predicting that `copy` also changes because `Clone` is shallow misreads the pitfall. Shallowness only matters when elements are references; for `int[]` the shallow copy already duplicates every value.

**How to verify.** Keep the `alias versus copy` check and add `Check(ReferenceEquals(alias, source) && !ReferenceEquals(copy, source), "identity")`. Both pass silently.

### Task 2: Guided modification

Change only the copied array and verify source is unchanged.

**Written answer.** After Example A, write `copy[1] = 7;` and check `source[1] == 4 && copy[1] == 7`. Only the cloned array receives the write.

**Why it is correct.** The clone owns its own two slots, so a write through `copy` cannot reach the storage that `source` and `alias` share.

**Plausible wrong approach.** Making the copy with `int[] copy = source;` instead of `Clone` creates a second alias. The write to `copy[1]` then changes `source[1]` to 7 and the new check throws.

**How to verify.** Run the corrected version and the check passes. Temporarily replace `(int[])source.Clone()` with plain assignment and confirm the same check now fails; that proves the check can tell a copy from an alias.

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

**Plausible wrong approach.** Using `grid.Length` as the row bound treats the 6 cells as 6 rows. The loop reaches `grid[2, 0]` and throws `IndexOutOfRangeException`, and `new int[grid.Length]` would also allocate six result slots for two rows.

**How to verify.** The block checks `rowSums` against `{ 6, 15 }`. Their total, 21, must also match Example B's `all six cells` sum, a cross-check that every cell was counted once.

### Task 4: Diagnose a defect

Diagnose a nested loop that uses the row count for both dimensions.

**Written answer.** The defect reads `col < grid.GetLength(0)` in the inner loop. On the 2 by 3 grid it visits only columns 0 and 1, so the sum is 1 + 2 + 4 + 5 = 12 instead of 21. The fix is `col < grid.GetLength(1)`.

**Why it is correct.** `GetLength(0)` is the row count and `GetLength(1)` the column count. Each loop bound must come from the dimension that its index variable addresses.

**Plausible wrong approach.** Testing the fix on a 3 by 3 grid proves nothing, because the buggy and correct bounds are both 3. Replacing the bound with `grid.Length` is also wrong: 6 overruns the column index and throws.

**How to verify.** With the bug, the `all six cells` check throws because the sum is 12. On a 3 by 2 grid the same bug throws `IndexOutOfRangeException` at column 2 instead. After the fix the sum is 21 and the check is silent.

### Task 5: Boundary evidence

Test an empty array and a one-row rectangular array.

**Written answer.** Check `int[] empty = Array.Empty<int>();` has `Length == 0` and that a summing loop over it returns 0. For `int[,] oneRow = { { 7, 8, 9 } };` check `GetLength(0) == 1`, `GetLength(1) == 3` and a row sum of 24.

**Why it is correct.** A loop bounded by `Length` or `GetLength` simply does not execute for size 0, and a single row keeps its own column count, so both shapes need no special branch.

**Plausible wrong approach.** Reading `empty[0]` as a default first value throws `IndexOutOfRangeException`. For the single row, using `oneRow.Length` as the row count gives 3 rows instead of 1 and overruns `oneRow[1, 0]`.

**How to verify.** All checks pass silently. Add `new int[0, 3]` as a third case: `GetLength(1)` is 3 while `Length` is 0, which shows shape and cell count are different facts.

### Task 6: Transfer and justify

Choose rectangular or jagged storage for variable-length sensor histories and justify the choice.

**Written answer.** Use jagged storage, `double[][] histories`, with one inner array per sensor, for example 3 readings for sensor 0 and 5 for sensor 1. Each row's own `Length` is its history length.

**Why it is correct.** A rectangular `double[,]` forces one column count on every row, so shorter histories would need padding. Jagged rows record each real length directly. The limitation is that inner arrays can be null and there is no single `GetLength(1)`, so code must check each row.

**Plausible wrong approach.** A `new double[sensors, 5]` array padded with zeros looks tidy, but sensor 0's mean is then computed over 5 slots, two of them fake zeros, and is understated. Padding with `NaN` instead silently poisons the sum.

**How to verify.** Check `histories[0].Length == 3 && histories[1].Length == 5`, and compute each mean by dividing by that row's own `Length`; compare with a hand calculation for both sensors.

## Mechanism and diagnostic reasoning

An array has a fixed number of elements with one element type. Its length does not grow after creation. Assignment copies the array reference, so two variables can refer to the same storage. A copied array can separate the outer storage while still sharing referenced elements. Before using a copy, identify which level of independence the algorithm needs.

A rectangular array has dimensions built into its shape; a jagged array is an array of arrays whose row lengths may differ. Data-science work often fails at shape boundaries before the numerical formula is wrong. Make row and column assumptions explicit and test a non-square fixture so swapping dimensions cannot accidentally pass.

`new int[3]` creates three zero-initialized entries. `values[0]` addresses the first. `int[,] grid` has rank two and GetLength selects a dimension. `int[][]` contains separate row arrays.

Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.

## Review before continuing

Run the reference and confirm that it prints `csharp-008: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
