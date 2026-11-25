# csharp-035: Span, slices and memory lifetime

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-034`

## Learning objectives

Use Span and ReadOnlySpan to slice data without copying while respecting their lifetime rules. The central exercise is task 3: Write a synchronous span helper counting separators.

## Purpose and mental model

Span<T> is a view over contiguous memory. A slice describes a region without copying its elements, so writes through a mutable span change the underlying storage. ReadOnlySpan prevents mutation through that view but does not freeze other aliases. This makes ownership and lifetime central to correct use.

Span is a ref struct with restrictions that prevent it from escaping into ordinary heap objects. It cannot be retained across an await boundary. Memory<T> can represent a heap-storable region for asynchronous APIs, but its owner still controls lifetime. Optimize allocations only after measuring; a span does not improve an algorithm whose complexity is the real bottleneck.

## Vocabulary and concepts

**Span:** A bounded view over contiguous memory.

**Slice:** A subregion sharing the same backing storage.

**Lifetime:** The period during which referenced storage remains valid.

## How to run this lesson

`DoubleMiddle` and `SumDigits` are synchronous helpers declared after `Main`. Spans are ref structs, so an async method cannot keep one alive across an `await`: the compiler reports CS4007, saying the instance cannot be preserved across the boundary. That is why span work sits in separate synchronous methods.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`array.AsSpan(start, length)` creates a view. `Slice` changes the viewed interval. `ReadOnlySpan<T>` narrows write capability. Keep synchronous span logic in a helper separate from async orchestration.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int[] values = { 1, 2, 3 };
      DoubleMiddle(values);
      Check(values.SequenceEqual(new[] { 1, 4, 3 }), "slice aliases array");
    }
    Console.WriteLine("csharp-035: passed");
    await Task.CompletedTask;
  }

  public static void DoubleMiddle(int[] values) {
    Span<int> middle = values.AsSpan(1, 1);
    middle[0] *= 2;
  }
  public static int SumDigits(ReadOnlySpan<char> text) {
    int total = 0;
    foreach (char ch in text) {
      if (ch < '0' || ch > '9')
        throw new ArgumentException("digits required");
      total += ch - '0';
    }
    return total;
  }
}
```

**Observe:** Only the middle element changes.

**Trace.** `values` holds 1, 2 and 3. Inside `DoubleMiddle`, `AsSpan(1, 1)` creates a view of one element starting at index 1, with no copy. `middle[0]` therefore refers to `values[1]`, and multiplying by two writes 4 into the array. After the call, the array reads 1, 4, 3, and the span itself no longer exists.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      Check(SumDigits("123".AsSpan()) == 6, "digit total");
      Check(SumDigits(ReadOnlySpan<char>.Empty) == 0, "empty identity");
    }
    Console.WriteLine("csharp-035: passed");
    await Task.CompletedTask;
  }

  public static void DoubleMiddle(int[] values) {
    Span<int> middle = values.AsSpan(1, 1);
    middle[0] *= 2;
  }
  public static int SumDigits(ReadOnlySpan<char> text) {
    int total = 0;
    foreach (char ch in text) {
      if (ch < '0' || ch > '9')
        throw new ArgumentException("digits required");
      total += ch - '0';
    }
    return total;
  }
}
```

**Observe:** The digit total is 6 and empty input totals zero.

**Trace.** `"123".AsSpan()` views the string's characters without allocating a substring. `SumDigits` walks the view: 1, 2 and 3 each pass the digit test and contribute `ch - '0'`, giving 6. `ReadOnlySpan<char>.Empty` has no characters, so the loop never runs and the result is 0. Text containing a letter throws `ArgumentException` from inside the loop.

## Exercises

1. **Predict and explain.** Draw the backing array and slice boundaries.

2. **Guided modification.** Change the slice to cover two elements.

3. **Independent construction.** Write a synchronous span helper counting separators.

4. **Diagnose a defect.** Diagnose retaining a span across await.

5. **Boundary evidence.** Test empty and out-of-range slices and distinguish valid empty from invalid bounds.

6. **Transfer and justify.** Choose Span or Memory for a synchronous parser and an asynchronous buffer owner.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.

For task 5, `values.AsSpan(1, 5)` on a three-element array throws `ArgumentOutOfRangeException`, while `values.AsSpan(3, 0)` is a valid empty span at the end. For task 4, holding a `Span<int>` across `await Task.Yield()` does not compile, with error CS4007; `Memory<int>` can be stored and awaited across instead.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Mutate through a view) before changing anything, and confirm its observation: Only the middle element changes.
2. Compare Example B (Parse without allocating substrings) with Example A and name the first line whose behavior differs. Its observation is: The digit total is 6 and empty input totals zero.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: ReadOnlySpan restricts this view, not every alias.

## Self-check and next step

Draw the array for Example A and mark the interval `AsSpan(1, 1)` covers. Explain why a `ReadOnlySpan<char>` over 123 can be summed without allocating. For task 6, decide whether a synchronous parser should take `Span<T>` or `Memory<T>`, and do the same for an asynchronous buffer owner.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/): The memory and spans guide explains `Span<T>`, `Memory<T>`, ownership rules and when each fits.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
