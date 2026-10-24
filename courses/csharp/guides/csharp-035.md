# csharp-035: Span, slices and memory lifetime

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-034`

## Learning objectives

Write a synchronous span helper counting separators. Then choose Span or Memory for a synchronous parser and an asynchronous buffer owner.

## Purpose and mental model

Span<T> is a view over contiguous memory. A slice describes a region without copying its elements, so writes through a mutable span change the underlying storage. ReadOnlySpan prevents mutation through that view but does not freeze other aliases. This makes ownership and lifetime central to correct use.

Span is a ref struct with restrictions that prevent it from escaping into ordinary heap objects. It cannot be retained across an await boundary. Memory<T> can represent a heap-storable region for asynchronous APIs, but its owner still controls lifetime. Optimize allocations only after measuring; a span does not improve an algorithm whose complexity is the real bottleneck.

## Vocabulary and concepts

**Span:** A bounded view over contiguous memory.

**Slice:** A subregion sharing the same backing storage.

**Lifetime:** The period during which referenced storage remains valid.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`array.AsSpan(start, length)` creates a view. `Slice` changes the viewed interval. `ReadOnlySpan<T>` narrows write capability. Keep synchronous span logic in a helper separate from async orchestration.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Mutate through a view

A span slice is a view, not a copy of the selected element.

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
            int[] values = { 1, 2, 3 };
            DoubleMiddle(values);
            Check(values.SequenceEqual(new[] { 1, 4, 3 }), "slice aliases array");
        }
        Console.WriteLine("csharp-035: passed");
        await Task.CompletedTask;
    }

    public static void DoubleMiddle(int[] values) { Span<int> middle = values.AsSpan(1, 1); middle[0] *= 2; }
    public static int SumDigits(ReadOnlySpan<char> text) { int total = 0; foreach (char ch in text) { if (ch < '0' || ch > '9') throw new ArgumentException("digits required"); total += ch - '0'; } return total; }
}
```

**Observe:** Only the middle element changes.

### Example B: Parse without allocating substrings

The helper reads directly from the character view and validates each admitted character.

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
            Check(SumDigits("123".AsSpan()) == 6, "digit total");
            Check(SumDigits(ReadOnlySpan<char>.Empty) == 0, "empty identity");
        }
        Console.WriteLine("csharp-035: passed");
        await Task.CompletedTask;
    }

    public static void DoubleMiddle(int[] values) { Span<int> middle = values.AsSpan(1, 1); middle[0] *= 2; }
    public static int SumDigits(ReadOnlySpan<char> text) { int total = 0; foreach (char ch in text) { if (ch < '0' || ch > '9') throw new ArgumentException("digits required"); total += ch - '0'; } return total; }
}
```

**Observe:** The digit total is 6 and empty input totals zero.

## Exercises

1. **Predict and explain.** Draw the backing array and slice boundaries.

2. **Guided modification.** Change the slice to cover two elements.

3. **Independent construction.** Write a synchronous span helper counting separators.

4. **Diagnose a defect.** Diagnose retaining a span across await.

5. **Boundary evidence.** Test empty and out-of-range slices and distinguish valid empty from invalid bounds.

6. **Transfer and justify.** Choose Span or Memory for a synchronous parser and an asynchronous buffer owner.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Span, Slice, Lifetime without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-035: Span, slices and memory lifetime.
Read courses/csharp/guides/csharp-035.md and courses/csharp/lessons/csharp-035.cs. Prerequisites: csharp-034.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-035_solution.cs and
courses/csharp/solutions/csharp-035_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
