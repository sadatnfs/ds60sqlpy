# csharp-020: LINQ, deferred execution and materialization

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-019`

## Learning objectives

Build a deterministic report selecting, transforming and ordering records. Then choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.

## Purpose and mental model

Language Integrated Query expresses sequence transformations such as filtering, projection and ordering. Many LINQ operators produce a recipe rather than immediately executing it. Enumeration runs that recipe. If the source changes before enumeration, the result can change too. This timing is part of the semantics, not an incidental optimization.

Materialization with ToArray or ToList executes a query and stores its current result. It consumes memory but creates a useful snapshot boundary. Repeatedly enumerating an expensive or stateful source can repeat work or observe different data. Decide whether the consumer needs a live recipe, a one-pass stream or a stable materialized result.

## Vocabulary and concepts

**Deferred execution:** Work performed when a sequence is enumerated.

**Projection:** Transforming each selected element.

**Materialization:** Executing and storing a sequence result.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Where` keeps matching elements; `Select` transforms each element. `OrderBy` chooses ordering. `ToArray` materializes. Lambdas used by deferred operators run during enumeration, so avoid hidden side effects.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Predict whether adding an item before enumeration affects query and snapshot.

2. **Guided modification.** Add a projection from integers to labeled strings.

3. **Independent construction.** Build a deterministic report selecting, transforming and ordering records.

4. **Diagnose a defect.** Diagnose a query with a side-effect counter enumerated twice.

5. **Boundary evidence.** Test empty input and a filter matching no rows.

6. **Transfer and justify.** Choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Deferred execution, Projection, Materialization without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
