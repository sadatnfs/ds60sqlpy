# csharp-009: Lists, capacity and safe mutation

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-008`

## Learning objectives

Filter and mutate lists safely, telling capacity from count and copies from in-place changes. The central exercise is task 3: Produce a filtered list while preserving the original.

## Purpose and mental model

A List stores a resizable indexed sequence. Count is the number of elements logically present; capacity is storage reserved to reduce reallocations. Increasing capacity does not create valid elements. Append is often efficient, but inserting at the front shifts existing entries. The interface makes these operations equally easy to write while their costs differ.

Enumeration assumes a stable collection structure. Removing items during foreach invalidates that assumption. Choose a bulk removal operation, construct a new result, or use a deliberate index strategy. The right choice depends on whether other parts of the program should observe mutation of the original list.

## Vocabulary and concepts

**Count:** The number of present elements.

**Capacity:** Allocated room available before growth.

**Snapshot:** A separately stored view captured at a moment.

## How to run this lesson

`List<T>`, `ToArray` and `SequenceEqual` need no extra using directives in the classroom project. Task 4's removal inside `foreach` throws `InvalidOperationException` saying the collection was modified, so wrap it in a `try` if you want the rest of your pad to keep running.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`new List<int> { ... }` uses a collection initializer. `Add` changes Count; an indexer replaces an existing element. `RemoveAll(predicate)` expresses structural removal as one owned operation. `ToArray` creates a snapshot of the element references or values.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `new List<int>(10)` reserves an internal array of ten slots but holds no elements, so `Count` is 0 and `Capacity` is at least 10. Each `Add` writes the next slot and increments Count: after adding 3 and 5, Count is 2 and index 1 holds 5. Reading index 2 throws `ArgumentOutOfRangeException` even though storage exists, because the indexer checks Count, not Capacity.

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

**Trace.** `ToArray()` copies the four integers into a new array before anything changes. `RemoveAll` then visits every element once, keeps those for which the predicate is false and compacts them, so the list becomes 2 and 4. It returns 2, the number removed. The snapshot `before` is separate storage and still holds all four values.

## Exercises

1. **Predict and explain.** Predict Count and Capacity before and after appends.

2. **Guided modification.** Replace one existing entry and explain why Count stays constant.

3. **Independent construction.** Produce a filtered list while preserving the original.

4. **Diagnose a defect.** Diagnose removing an entry inside foreach.

5. **Boundary evidence.** Test no removals, all removals and an empty list.

6. **Transfer and justify.** Choose mutation or a new sequence for an undoable editor operation and explain who observes the change.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.

Adding an eleventh element to a list created with capacity 10 grows Capacity to 20 in this runtime, but no contract promises that growth factor, so never test for it. For task 5, an all-negative input must leave an empty list and return its original count, and an empty list must return 0 without throwing.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Separate count from reserved storage) before changing anything, and confirm its observation: Reserving ten slots leaves Count at zero; two appends produce Count two.
2. Compare Example B (Remove under one mutation policy) with Example A and name the first line whose behavior differs. Its observation is: Two entries are removed while the earlier integer snapshot keeps four values.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Capacity is not an index boundary.

## Self-check and next step

Predict Count and Capacity after constructing `new List<int>(4)` and adding five values, and say which of those two numbers your code may rely on. Explain why `RemoveAll` is safe where removing inside `foreach` is not. For task 6, say who observes an in-place change and who observes a new list.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `List<T>` API reference documents `Capacity`, `Count`, `RemoveAll` and how its enumerator reacts when the list changes.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
