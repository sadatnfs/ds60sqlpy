# csharp-008: Arrays, indices and rectangular data

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-007`

## Learning objectives

Compute each row sum of the two-by-three grid. Then choose rectangular or jagged storage for variable-length sensor histories and justify the choice.

## Purpose and mental model

An array has a fixed number of elements with one element type. Its length does not grow after creation. Assignment copies the array reference, so two variables can refer to the same storage. A copied array can separate the outer storage while still sharing referenced elements. Before using a copy, identify which level of independence the algorithm needs.

A rectangular array has dimensions built into its shape; a jagged array is an array of arrays whose row lengths may differ. Data-science work often fails at shape boundaries before the numerical formula is wrong. Make row and column assumptions explicit and test a non-square fixture so swapping dimensions cannot accidentally pass.

## Vocabulary and concepts

**Array:** Fixed-length indexed element storage.

**Alias:** Another reference to the same storage.

**Shape:** The size and organization of dimensions.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`new int[3]` creates three zero-initialized entries. `values[0]` addresses the first. `int[,] grid` has rank two and GetLength selects a dimension. `int[][]` contains separate row arrays.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            int[,] grid = { { 1, 2, 3 }, { 4, 5, 6 } };
            Check(grid.GetLength(0) == 2 && grid.GetLength(1) == 3, "rectangular shape");
            int sum = 0;
            for (int row = 0; row < grid.GetLength(0); row++) for (int col = 0; col < grid.GetLength(1); col++) sum += grid[row, col];
            Check(sum == 21, "all six cells");
        }
        Console.WriteLine("csharp-008: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The shape is two by three and the sum is 21.

## Exercises

1. **Predict and explain.** Predict source and copy after alias mutation.

2. **Guided modification.** Change only the copied array and verify source is unchanged.

3. **Independent construction.** Compute each row sum of the two-by-three grid.

4. **Diagnose a defect.** Diagnose a nested loop that uses the row count for both dimensions.

5. **Boundary evidence.** Test an empty array and a one-row rectangular array.

6. **Transfer and justify.** Choose rectangular or jagged storage for variable-length sensor histories and justify the choice.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Array, Alias, Shape without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
