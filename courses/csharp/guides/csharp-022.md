# csharp-022: Iterators and lazy sequence contracts

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-021`

## Learning objectives

Write lazy iterators with yield return and validate their arguments at the call boundary. The central exercise is task 3: Implement a lazy sequence of cumulative totals.

## Purpose and mental model

An iterator describes a sequence whose values are produced as the consumer asks for them. It can avoid materializing a large collection and can stop work when the consumer stops early. `yield return` pauses the iterator with its local state retained; the next request resumes it. This is different from returning a fully constructed list.

Lazy code shifts both work and some errors into enumeration. If argument validation must happen at the call site, place it outside the iterator body and return a nested iterator. Resource-owning iterators must also release resources when enumeration is abandoned. Consumers using foreach receive disposal behavior; custom enumerator handling must preserve it.

## Vocabulary and concepts

**Iterator:** A stateful producer of successive values.

**Enumeration:** Repeatedly requesting the next element.

**Laziness:** Deferring work until a consumer demands it.

## How to run this lesson

`RangeFrom` validates its argument and then returns a nested local iterator, `Iterate`, which holds the `yield return` loop. Calling `RangeFrom(0, -1)` throws immediately; if you move the check into `Iterate`, the call returns without throwing and the error appears only when something enumerates the sequence.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`IEnumerable<int>` exposes an iterable sequence. `yield return value` supplies one element and suspends. A nested local iterator separates immediate argument validation from delayed generation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Consume only a prefix

The producer does not need to allocate all four outputs before serving the first one.

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
      Check(RangeFrom(5, 4).Take(2).SequenceEqual(new[] { 5, 6 }),
            "bounded prefix");
      Check(!RangeFrom(5, 0).Any(), "empty range");
    }
    Console.WriteLine("csharp-022: passed");
    await Task.CompletedTask;
  }

  public static IEnumerable<int> RangeFrom(int start, int count) {
    if (count < 0)
      throw new ArgumentOutOfRangeException(nameof(count));
    return Iterate();
    IEnumerable<int> Iterate() {
      for (int i = 0; i < count; i++)
        yield return checked(start + i);
    }
  }
}
```

**Observe:** The consumer receives 5 and 6 and can stop before the full range.

**Trace.** `RangeFrom(5, 4)` validates the count and returns the iterator without running the loop. `Take(2)` requests a first element: the loop starts, yields 5 and suspends. It requests a second and gets 6. Take then stops asking, so 7 and 8 are never produced. `RangeFrom(5, 0).Any()` finds an empty sequence and returns false.

### Example B: Validate before returning the sequence

The outer method validates first; the local iterator performs only the admitted traversal.

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
      bool rejected = false;
      try {
        _ = RangeFrom(0, -1);
      } catch (ArgumentOutOfRangeException) {
        rejected = true;
      }
      Check(rejected, "validation occurs at call boundary");
      Check(RangeFrom(2, 3).Sum() == 9, "complete enumeration");
    }
    Console.WriteLine("csharp-022: passed");
    await Task.CompletedTask;
  }

  public static IEnumerable<int> RangeFrom(int start, int count) {
    if (count < 0)
      throw new ArgumentOutOfRangeException(nameof(count));
    return Iterate();
    IEnumerable<int> Iterate() {
      for (int i = 0; i < count; i++)
        yield return checked(start + i);
    }
  }
}
```

**Observe:** Negative count is rejected immediately, without enumeration.

**Trace.** `RangeFrom(0, -1)` reaches the guard in the outer method and throws `ArgumentOutOfRangeException` at the call, even though the result is discarded and never enumerated. `RangeFrom(2, 3).Sum()` enumerates the full sequence 2, 3 and 4, and the sum is 9. The outer method runs eagerly; only the local iterator is lazy.

## Exercises

1. **Predict and explain.** Trace how many values Take(2) requests.

2. **Guided modification.** Generate every second integer with a bounded count.

3. **Independent construction.** Implement a lazy sequence of cumulative totals.

4. **Diagnose a defect.** Diagnose validation inside an iterator body that callers expect to run immediately.

5. **Boundary evidence.** Test count zero, one and negative.

6. **Transfer and justify.** Choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.

For task 4, place the count check inside the iterator body: `var seq = Bad(-1);` then completes without error and the exception surfaces only at `seq.ToArray()`, possibly far from the call that passed the bad value. For task 5, count 1 yields exactly the start value, and count 0 yields nothing without throwing.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Consume only a prefix) before changing anything, and confirm its observation: The consumer receives 5 and 6 and can stop before the full range.
2. Compare Example B (Validate before returning the sequence) with Example A and name the first line whose behavior differs. Its observation is: Negative count is rejected immediately, without enumeration.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A sequence is not necessarily repeatable or cheap to enumerate.

## Self-check and next step

Explain how many times the loop body in `Iterate` runs for `RangeFrom(5, 4).Take(2).ToArray()`. Say why the guard lives outside the iterator. For task 6, describe what happens to an open file if a caller enumerates a file-reading sequence twice or abandons it halfway.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# reference on the `yield` statement and on iterators explains how the compiler turns an iterator method into a lazily run state machine.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-022: Iterators and lazy sequence contracts.
Read courses/csharp/guides/csharp-022.md and courses/csharp/lessons/csharp-022.cs. Prerequisites: csharp-021.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-022_solution.cs and
courses/csharp/solutions/csharp-022_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
