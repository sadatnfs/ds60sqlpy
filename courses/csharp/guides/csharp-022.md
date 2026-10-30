# csharp-022: Iterators and lazy sequence contracts

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-021`

## Learning objectives

Implement a lazy sequence of cumulative totals. Then choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.

## Purpose and mental model

An iterator describes a sequence whose values are produced as the consumer asks for them. It can avoid materializing a large collection and can stop work when the consumer stops early. `yield return` pauses the iterator with its local state retained; the next request resumes it. This is different from returning a fully constructed list.

Lazy code shifts both work and some errors into enumeration. If argument validation must happen at the call site, place it outside the iterator body and return a nested iterator. Resource-owning iterators must also release resources when enumeration is abandoned. Consumers using foreach receive disposal behavior; custom enumerator handling must preserve it.

## Vocabulary and concepts

**Iterator:** A stateful producer of successive values.

**Enumeration:** Repeatedly requesting the next element.

**Laziness:** Deferring work until a consumer demands it.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`IEnumerable<int>` exposes an iterable sequence. `yield return value` supplies one element and suspends. A nested local iterator separates immediate argument validation from delayed generation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Trace how many values Take(2) requests.

2. **Guided modification.** Generate every second integer with a bounded count.

3. **Independent construction.** Implement a lazy sequence of cumulative totals.

4. **Diagnose a defect.** Diagnose validation inside an iterator body that callers expect to run immediately.

5. **Boundary evidence.** Test count zero, one and negative.

6. **Transfer and justify.** Choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Iterator, Enumeration, Laziness without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
