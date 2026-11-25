# csharp-008: Arrays, indices and rectangular data

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-007`

## Learning objectives

Tell array aliases from copies and traverse rectangular arrays with bounds taken from the data. The central exercise is task 3: Compute each row sum of the two-by-three grid.

## Purpose and mental model

An array has a fixed number of elements with one element type. Its length does not grow after creation. Assignment copies the array reference, so two variables can refer to the same storage. A copied array can separate the outer storage while still sharing referenced elements. Before using a copy, identify which level of independence the algorithm needs.

A rectangular array has dimensions built into its shape; a jagged array is an array of arrays whose row lengths may differ. Data-science work often fails at shape boundaries before the numerical formula is wrong. Make row and column assumptions explicit and test a non-square fixture so swapping dimensions cannot accidentally pass.

## Vocabulary and concepts

**Array:** Fixed-length indexed element storage.

**Alias:** Another reference to the same storage.

**Shape:** The size and organization of dimensions.

## How to run this lesson

Example B's nested loop sits on one line of source; rewrite it across several lines in a scratch pad if that is easier to trace. For task 5, an empty rectangular array such as `new int[0, 3]` is legal: its `Length` is 0 while `GetLength(1)` still reports 3.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`new int[3]` creates three zero-initialized entries. `values[0]` addresses the first. `int[,] grid` has rank two and GetLength selects a dimension. `int[][]` contains separate row arrays.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Copy the storage deliberately

Primitive elements are values, so cloning this array provides independent element storage.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int[] source = { 2, 4 };
      int[] alias = source;
      int[] copy = (int[])source.Clone();
      alias[0] = 9;
      Check(source[0] == 9 && copy[0] == 2, "alias versus copy");
    }
    Console.WriteLine("csharp-008: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The alias changes source; the copied integer array retains 2.

**Trace.** `source` refers to a new array holding 2 and 4. `alias = source` copies the reference, so both names point to one array. `Clone()` allocates a second array and copies the two integers into it, and the cast restores the `int[]` type. Writing 9 through `alias` changes the shared array, so `source[0]` reads 9 while `copy[0]` still reads 2.

### Example B: Respect distinct dimensions

Different dimension sizes expose swapped-boundary mistakes that a square fixture can hide.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int[,] grid = { { 1, 2, 3 }, { 4, 5, 6 } };
      Check(grid.GetLength(0) == 2 && grid.GetLength(1) == 3,
            "rectangular shape");
      int sum = 0;
      for (int row = 0; row < grid.GetLength(0); row++)
        for (int col = 0; col < grid.GetLength(1); col++)
          sum += grid[row, col];
      Check(sum == 21, "all six cells");
    }
    Console.WriteLine("csharp-008: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The shape is two by three and the sum is 21.

**Trace.** `GetLength(0)` returns 2 rows and `GetLength(1)` returns 3 columns. The outer loop fixes a row and the inner loop visits each column of it: 1, 2 and 3 give 6, then 4, 5 and 6 add 15, so `sum` ends at 21. Using `grid.Length`, which is 6, as the bound for either loop would run past that dimension.

## Exercises

1. **Predict and explain.** Predict source and copy after alias mutation.

2. **Guided modification.** Change only the copied array and verify source is unchanged.

3. **Independent construction.** Compute each row sum of the two-by-three grid.

4. **Diagnose a defect.** Diagnose a nested loop that uses the row count for both dimensions.

5. **Boundary evidence.** Test an empty array and a one-row rectangular array.

6. **Transfer and justify.** Choose rectangular or jagged storage for variable-length sensor histories and justify the choice.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.

Task 4's loop that uses `GetLength(0)` for both bounds visits only columns 0 and 1 of the two-by-three grid; it misses 3 and 6 and returns 12 without throwing. A three-by-two grid throws instead, so test both shapes. For task 1, remember that cloning an array of objects copies only the references, so a shared object would still change.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Copy the storage deliberately) before changing anything, and confirm its observation: The alias changes source; the copied integer array retains 2.
2. Compare Example B (Respect distinct dimensions) with Example A and name the first line whose behavior differs. Its observation is: The shape is two by three and the sum is 21.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Clone is shallow for referenced elements.

## Self-check and next step

Draw `source`, `alias` and `copy` after `alias[0] = 9`, showing which names share storage. Give `Length` and both `GetLength` values for a three-by-four rectangular array. Explain when a jagged `int[][]` fits variable-length rows better than `int[,]`, and what a jagged array costs when every row has the same length.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The reference article on arrays covers single-dimensional, multidimensional and jagged arrays and their properties.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-008: Arrays, indices and rectangular data.
Read courses/csharp/guides/csharp-008.md and courses/csharp/lessons/csharp-008.cs. Prerequisites: csharp-007.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-008_solution.cs and
courses/csharp/solutions/csharp-008_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
