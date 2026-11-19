# csharp-010: Dictionaries, sets and identity policies

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-009`

## Learning objectives

Count and deduplicate with dictionaries and sets under an explicit comparer, keeping a present zero distinct from absence. The central exercise is task 3: Build a frequency dictionary from a list of tags.

## Purpose and mental model

A dictionary maps unique keys to values. A set represents membership without duplicates. Their behavior depends on equality and hashing: values considered equal must have compatible hash codes. Choosing a string comparer is therefore a data-model decision, not just a search convenience. Machine identifiers may be case-sensitive or case-insensitive depending on the contract.

A missing key is different from a present key holding a default value. Use TryGetValue when absence is expected. Sorting output separately from lookup makes demonstrations deterministic without claiming that dictionary iteration order is the business ordering. If order matters, encode that requirement explicitly.

## Vocabulary and concepts

**Key:** The identity used for lookup.

**Hashing:** A mapping that narrows candidate equality comparisons.

**Membership:** Whether an equivalent element belongs to a set.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Dictionary<string,int>(StringComparer.OrdinalIgnoreCase)` defines key identity. `TryGetValue(key, out value)` separates absence from a stored zero. `HashSet<T>.Add` returns whether membership changed.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Preserve absence information

The comparer belongs to the collection contract. A missing value cannot be inferred from the integer alone.

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
      var counts = new Dictionary<string, int>(
          StringComparer.OrdinalIgnoreCase) { ["Oak"] = 0 };
      Check(counts.TryGetValue("OAK", out int zero) && zero == 0,
            "present zero");
      Check(!counts.TryGetValue("Pine", out _), "missing key");
    }
    Console.WriteLine("csharp-010: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** OAK finds a present zero; Pine is absent.

### Example B: Deduplicate by an explicit policy

Deduplication is meaningful only after defining equality. Case-insensitive comparison is appropriate for this fixture, not for every identifier.

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
      var labels = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
      Check(labels.Add("red"), "first insertion");
      Check(!labels.Add("RED"), "duplicate identity");
      labels.Add("blue");
      Check(labels.Count == 2, "two identities");
    }
    Console.WriteLine("csharp-010: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** RED is a duplicate under the selected comparer.

## Exercises

1. **Predict and explain.** Predict the difference between absent Pine and present-zero Oak.

2. **Guided modification.** Switch to an ordinal case-sensitive comparer and explain the changed lookup.

3. **Independent construction.** Build a frequency dictionary from a list of tags.

4. **Diagnose a defect.** Diagnose indexing a missing key without an absence policy.

5. **Boundary evidence.** Test empty tags, repeated tags and keys differing only by case.

6. **Transfer and justify.** Design stable identity for records and explain which fields may change without invalidating lookup.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. The separate explanation gives an executed reference answer where one has been written and says plainly where none exists yet. Open it only after your own attempt, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Reproduce Example A (Preserve absence information) before changing anything, and confirm its observation: OAK finds a present zero; Pine is absent.
2. Compare Example B (Deduplicate by an explicit policy) with Example A and name the first line whose behavior differs. Its observation is: RED is a duplicate under the selected comparer.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Changing a key field after insertion can break hash-based lookup for mutable custom keys.

## Self-check and next step

Explain Key, Hashing, Membership without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-010: Dictionaries, sets and identity policies.
Read courses/csharp/guides/csharp-010.md and courses/csharp/lessons/csharp-010.cs. Prerequisites: csharp-009.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-010_solution.cs and
courses/csharp/solutions/csharp-010_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
