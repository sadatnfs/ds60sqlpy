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

Both examples pass an explicit comparer to the collection constructor, and every later lookup uses it. For task 2, construct the dictionary without a comparer, which defaults to ordinal case-sensitive equality, and run the same `TryGetValue("OAK", ...)` call; it then returns false.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Dictionary<string,int>(StringComparer.OrdinalIgnoreCase)` defines key identity. `TryGetValue(key, out value)` separates absence from a stored zero. `HashSet<T>.Add` returns whether membership changed.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** The initializer stores the key Oak with the value 0 under `OrdinalIgnoreCase`. `TryGetValue("OAK", out int zero)` hashes OAK with that comparer, finds Oak, writes 0 into `zero` and returns true. For Pine it finds nothing, still writes 0 to the output and returns false. Only the Boolean separates a stored zero from an absent key.

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

**Trace.** The set uses the case-insensitive comparer. `Add("red")` inserts the label and returns true. `Add("RED")` finds an equal element, leaves the set unchanged and returns false. `Add("blue")` inserts a second identity, so Count is 2. Under the default ordinal comparer, RED would have become a third member. The comparer is fixed at construction, so it cannot be changed later.

## Exercises

1. **Predict and explain.** Predict the difference between absent Pine and present-zero Oak.

2. **Guided modification.** Switch to an ordinal case-sensitive comparer and explain the changed lookup.

3. **Independent construction.** Build a frequency dictionary from a list of tags.

4. **Diagnose a defect.** Diagnose indexing a missing key without an absence policy.

5. **Boundary evidence.** Test empty tags, repeated tags and keys differing only by case.

6. **Transfer and justify.** Design stable identity for records and explain which fields may change without invalidating lookup.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.

Task 4's direct indexer `counts["Pine"]` throws `KeyNotFoundException`, saying the key was not present. Returning 0 there instead would make Pine look counted. For task 5, the tags a, A and a should produce one key with count 3 under the case-insensitive comparer and two keys under the default comparer.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve absence information) before changing anything, and confirm its observation: OAK finds a present zero; Pine is absent.
2. Compare Example B (Deduplicate by an explicit policy) with Example A and name the first line whose behavior differs. Its observation is: RED is a duplicate under the selected comparer.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Changing a key field after insertion can break hash-based lookup for mutable custom keys.

## Self-check and next step

Explain why `TryGetValue` returns a Boolean when its output value is filled in either way. Predict `Count` after adding red, RED, Red and blue to a case-insensitive set and to a default set. Describe what breaks if a custom key changes a field used by its hash code after insertion.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `Dictionary<TKey,TValue>` and `HashSet<T>` reference pages describe comparers, `TryGetValue` and the return value of `Add`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
