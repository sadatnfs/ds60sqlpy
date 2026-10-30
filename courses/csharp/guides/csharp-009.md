# csharp-009: Lists, capacity and safe mutation

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-008`

## Learning objectives

Produce a filtered list while preserving the original. Then choose mutation or a new sequence for an undoable editor operation and explain who observes the change.

## Purpose and mental model

A List stores a resizable indexed sequence. Count is the number of elements logically present; capacity is storage reserved to reduce reallocations. Increasing capacity does not create valid elements. Append is often efficient, but inserting at the front shifts existing entries. The interface makes these operations equally easy to write while their costs differ.

Enumeration assumes a stable collection structure. Removing items during foreach invalidates that assumption. Choose a bulk removal operation, construct a new result, or use a deliberate index strategy. The right choice depends on whether other parts of the program should observe mutation of the original list.

## Vocabulary and concepts

**Count:** The number of present elements.

**Capacity:** Allocated room available before growth.

**Snapshot:** A separately stored view captured at a moment.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`new List<int> { ... }` uses a collection initializer. `Add` changes Count; an indexer replaces an existing element. `RemoveAll(predicate)` expresses structural removal as one owned operation. `ToArray` creates a snapshot of the element references or values.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Separate count from reserved storage

Capacity is an implementation resource, not a promise that ten logical entries exist.

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
      var values = new List<int>(10);
      Check(values.Count == 0 && values.Capacity >= 10,
            "capacity is not count");
      values.Add(3);
      values.Add(5);
      Check(values.Count == 2 && values[1] == 5, "append order");
    }
    Console.WriteLine("csharp-009: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Reserving ten slots leaves Count at zero; two appends produce Count two.

### Example B: Remove under one mutation policy

A bulk operation owns traversal and mutation, avoiding an invalidated external enumerator.

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
      var values = new List<int> { -1, 2, -3, 4 };
      int[] before = values.ToArray();
      int removed = values.RemoveAll(value => value < 0);
      Check(removed == 2 && values.SequenceEqual(new[] { 2, 4 }),
            "filtered mutation");
      Check(before.Length == 4, "snapshot retained");
    }
    Console.WriteLine("csharp-009: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Two entries are removed while the earlier integer snapshot keeps four values.

## Exercises

1. **Predict and explain.** Predict Count and Capacity before and after appends.

2. **Guided modification.** Replace one existing entry and explain why Count stays constant.

3. **Independent construction.** Produce a filtered list while preserving the original.

4. **Diagnose a defect.** Diagnose removing an entry inside foreach.

5. **Boundary evidence.** Test no removals, all removals and an empty list.

6. **Transfer and justify.** Choose mutation or a new sequence for an undoable editor operation and explain who observes the change.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Count, Capacity, Snapshot without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-009: Lists, capacity and safe mutation.
Read courses/csharp/guides/csharp-009.md and courses/csharp/lessons/csharp-009.cs. Prerequisites: csharp-008.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-009_solution.cs and
courses/csharp/solutions/csharp-009_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
