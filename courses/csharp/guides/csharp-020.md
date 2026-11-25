# csharp-020: LINQ, deferred execution and materialization

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-019`

## Learning objectives

Write LINQ queries and predict when deferred execution observes later source changes. The central exercise is task 3: Build a deterministic report selecting, transforming and ordering records.

## Purpose and mental model

Language Integrated Query expresses sequence transformations such as filtering, projection and ordering. Many LINQ operators produce a recipe rather than immediately executing it. Enumeration runs that recipe. If the source changes before enumeration, the result can change too. This timing is part of the semantics, not an incidental optimization.

Materialization with ToArray or ToList executes a query and stores its current result. It consumes memory but creates a useful snapshot boundary. Repeatedly enumerating an expensive or stateful source can repeat work or observe different data. Decide whether the consumer needs a live recipe, a one-pass stream or a stable materialized result.

## Vocabulary and concepts

**Deferred execution:** Work performed when a sequence is enumerated.

**Projection:** Transforming each selected element.

**Materialization:** Executing and storing a sequence result.

## How to run this lesson

LINQ operators come from `System.Linq`, already in scope. Task 4's side-effect counter is the clearest experiment: a `Where` predicate that increments a counter, enumerated twice over three values with `Count()`, leaves the counter at 6, because each enumeration reruns the predicate on every element.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Where` keeps matching elements; `Select` transforms each element. `OrderBy` chooses ordering. `ToArray` materializes. Lambdas used by deferred operators run during enumeration, so avoid hidden side effects.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Observe query timing

Constructing Where does not copy the source values.

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
      var values = new List<int> { 1, 2 };
      var query = values.Where(value => value > 1);
      values.Add(3);
      Check(query.SequenceEqual(new[] { 2, 3 }),
            "query sees later source state");
    }
    Console.WriteLine("csharp-020: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The deferred query sees the subsequently appended 3.

**Trace.** `values` holds 1 and 2. `values.Where(...)` builds a query object and runs nothing. `values.Add(3)` changes the list. Only `SequenceEqual` enumerates the query, and at that moment the predicate sees 1, 2 and 3 and keeps 2 and 3. The query stores the recipe; the data is read when someone iterates.

### Example B: Capture a stable result

Materialization creates a deliberate temporal boundary while preserving the original list separately.

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
      var values = new List<int> { 1, 2 };
      int[] snapshot = values.Where(value => value > 1).ToArray();
      values.Add(3);
      Check(snapshot.SequenceEqual(new[] { 2 }), "snapshot remains stable");
      Check(values.Select(value => value * 10).ToArray().Length == 3,
            "projection count");
    }
    Console.WriteLine("csharp-020: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The earlier snapshot contains only 2 while a new projection sees three values.

**Trace.** This time `ToArray()` runs the filter immediately and copies the matching value, 2, into a new array. Adding 3 afterward changes the list but not `snapshot`, which still holds only 2. The second check builds a fresh `Select` over the list, materializes it and finds three projected values, because it runs after the append.

## Exercises

1. **Predict and explain.** Predict whether adding an item before enumeration affects query and snapshot.

2. **Guided modification.** Add a projection from integers to labeled strings.

3. **Independent construction.** Build a deterministic report selecting, transforming and ordering records.

4. **Diagnose a defect.** Diagnose a query with a side-effect counter enumerated twice.

5. **Boundary evidence.** Test empty input and a filter matching no rows.

6. **Transfer and justify.** Choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.

For task 5, a filter matching no rows returns an empty sequence, not null, so `Count()` is 0 and `First()` would throw. A deferred query over a list that is modified during enumeration throws `InvalidOperationException` at that later iteration, so the stack trace points at the loop rather than at the line that built the query.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe query timing) before changing anything, and confirm its observation: The deferred query sees the subsequently appended 3.
2. Compare Example B (Capture a stable result) with Example A and name the first line whose behavior differs. Its observation is: The earlier snapshot contains only 2 while a new projection sees three values.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: LINQ syntax does not imply database execution.

## Self-check and next step

For Example A, say when the predicate runs and how many times it runs in total. Explain what `ToArray()` changes about timing. For task 6, compare memory use and repeatability when an import streams rows through a query versus materializing all of them first.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The LINQ overview in the C# documentation explains deferred and immediate execution and the standard query operators.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-020: LINQ, deferred execution and materialization.
Read courses/csharp/guides/csharp-020.md and courses/csharp/lessons/csharp-020.cs. Prerequisites: csharp-019.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-020_solution.cs and
courses/csharp/solutions/csharp-020_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
