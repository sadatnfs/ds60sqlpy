# csharp-014: Records, structs and data equality

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-013`

## Learning objectives

Design an immutable coordinate using a readonly record struct. Then choose identity-based or data-based equality for an order and explain how updates affect collection membership.

## Purpose and mental model

Records describe data with synthesized equality and convenient copying. A record class still has reference identity, but its equality normally compares declared data members. A record struct is a value type. These features reduce boilerplate; they do not automatically make nested objects immutable or define the correct business identity.

A with expression constructs a copy with selected changes. That copy is shallow for referenced members. When a record contains a mutable list, two record instances may still share that list. Use immutable representations or deliberate copying when independent history is required. Choose equality fields from the domain rather than accepting every field merely because generation is convenient.

## Vocabulary and concepts

**Record:** A data-focused type with synthesized equality members.

**With expression:** A copy with selected member changes.

**Shallow copy:** A copy that retains references to nested objects.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`record Person(string Name, int Age)` declares positional properties and value-based equality. `record struct` changes assignment semantics. `with { Age = 31 }` creates a changed copy. `==` on records follows generated value equality.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Equal data with distinct identities

Value equality and reference identity answer different questions.

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
      var first = new Person("Ada", 30);
      var second = new Person("Ada", 30);
      Check(first == second, "record value equality");
      Check(!ReferenceEquals(first, second), "distinct objects");
      var older = first with { Age = 31 };
      Check(first.Age == 30 && older.Age == 31, "copy retains prior value");
    }
    Console.WriteLine("csharp-014: passed");
    await Task.CompletedTask;
  }

  public record Person(string Name, int Age);
  public record Basket(List<int> Items);
}
```

**Observe:** Equal records can be distinct objects; with preserves the previous age.

### Example B: Notice nested shared state

The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise.

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
      var first = new Basket(new List<int> { 1 });
      var second = first with {};
      second.Items.Add(2);
      Check(first.Items.Count == 2, "nested list is shared");
      Check(ReferenceEquals(first.Items, second.Items),
            "shallow copied member");
    }
    Console.WriteLine("csharp-014: passed");
    await Task.CompletedTask;
  }

  public record Person(string Name, int Age);
  public record Basket(List<int> Items);
}
```

**Observe:** Both records see the appended list item.

## Exercises

1. **Predict and explain.** Predict record equality and reference equality separately.

2. **Guided modification.** Create a changed copy with a new name and retain the original.

3. **Independent construction.** Design an immutable coordinate using a readonly record struct.

4. **Diagnose a defect.** Diagnose a supposedly immutable history entry containing a mutable list.

5. **Boundary evidence.** Compare records whose nested collections contain equal values but have different identities.

6. **Transfer and justify.** Choose identity-based or data-based equality for an order and explain how updates affect collection membership.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Record, With expression, Shallow copy without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-014: Records, structs and data equality.
Read courses/csharp/guides/csharp-014.md and courses/csharp/lessons/csharp-014.cs. Prerequisites: csharp-013.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-014_solution.cs and
courses/csharp/solutions/csharp-014_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
