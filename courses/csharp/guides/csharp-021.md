# csharp-021: Grouping, joins and data grain

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-020`

## Learning objectives

Group and join data at an explicit grain without duplicating or dropping records. The central exercise is task 3: Build a report joining unique item metadata to item totals.

## Purpose and mental model

Aggregation changes the grain of data. A row-per-event input can become a row-per-category result. State that grain before writing GroupBy so the result keys and totals have a meaning. Joining two sequences can multiply rows when keys are duplicated. This is a modeling issue that appears in LINQ just as it does in SQL.

An inner join drops keys with no partner. A left join needs an explicit absence policy. Before trusting a total after a join, inspect key uniqueness and count the expected matches. A tiny fixture with duplicate keys reveals accidental multiplication far more clearly than a large realistic dataset.

## Vocabulary and concepts

**Grain:** What one row or result item represents.

**Cardinality:** The number of records or matches.

**Join key:** The identity relating two datasets.

## How to run this lesson

Both examples use tuples with named elements, such as `Kind` and `Amount`, instead of declaring row classes. For task 4, `ToDictionary` over duplicate keys throws `ArgumentException` with the message that an item with the same key has already been added, which is usually the first sign of an unexpected duplicate.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`GroupBy(keySelector)` returns groups with Key and enumerable members. `Join` uses one key selector per side. A grouped lookup such as ToLookup preserves all matches, while ToDictionary requires unique keys.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Aggregate at a declared grain

Grouping changes grain while preserving the sum across all groups.

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
      var rows = new[] { (Kind: "a", Amount: 2), (Kind: "a", Amount: 3),
                         (Kind: "b", Amount: 4) };
      var totals = rows.GroupBy(row => row.Kind)
                       .ToDictionary(group => group.Key,
                                     group => group.Sum(row => row.Amount));
      Check(totals["a"] == 5 && totals["b"] == 4, "one total per kind");
    }
    Console.WriteLine("csharp-021: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Three event rows become two category totals.

**Trace.** The input grain is one row per event: three rows. `GroupBy(row => row.Kind)` forms group a with amounts 2 and 3 and group b with 4. `ToDictionary` takes each group's Key and the sum of its amounts, giving 5 for a and 4 for b. The output grain is one row per kind, and the grand total, 9, is unchanged.

### Example B: Expose duplicate-key multiplication

A key relationship does not imply one-to-one cardinality. Validate uniqueness if the domain requires exactly one match.

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
      var left = new[] { (Key: 1, Label: "L") };
      var right = new[] { (Key: 1, Value: "x"), (Key: 1, Value: "y") };
      var joined = left.Join(right, item => item.Key, item => item.Key,
                             (a, b) => a.Label + b.Value)
                       .ToArray();
      Check(joined.SequenceEqual(new[] { "Lx", "Ly" }), "two right matches");
    }
    Console.WriteLine("csharp-021: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** One left row becomes two joined rows.

**Trace.** `left` has one row with key 1, and `right` has two rows with key 1. `Join` pairs each left row with every right row whose key matches, so it produces two results, Lx and Ly. The output has more rows than the left input, and summing a left-side amount after this join would count it twice.

## Exercises

1. **Predict and explain.** State the input and output grain for each example.

2. **Guided modification.** Add a third category and verify total conservation.

3. **Independent construction.** Build a report joining unique item metadata to item totals.

4. **Diagnose a defect.** Diagnose a doubled total caused by duplicate metadata keys.

5. **Boundary evidence.** Test an unmatched key and choose an explicit handling policy.

6. **Transfer and justify.** Design checks that distinguish one-to-one, one-to-many and many-to-many joins before aggregation.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Aggregating after an unintended many-to-many join can inflate totals. ToDictionary throws on duplicate keys rather than choosing a winner. Sorting is needed when presentation order is part of the contract.

For task 4, duplicate metadata rows for one item turn a single total into two joined rows, so a sum after the join doubles. Check `GroupBy(key).Any(g => g.Count() > 1)` on the side that should be unique. For task 5, `Join` drops an unmatched key silently, while `ToLookup` returns an empty group for a missing key instead of throwing.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Aggregate at a declared grain) before changing anything, and confirm its observation: Three event rows become two category totals.
2. Compare Example B (Expose duplicate-key multiplication) with Example A and name the first line whose behavior differs. Its observation is: One left row becomes two joined rows.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Aggregating after an unintended many-to-many join can inflate totals.

## Self-check and next step

State the input and output grain for both examples and the total that must be conserved in Example A. Explain why `Join` can return more rows than either input. For task 6, describe one check that tells a one-to-many relationship from a many-to-many one before you aggregate.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): LINQ's grouping and join operations are covered in the standard query operator articles, including `GroupBy`, `Join` and `ToLookup`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-021: Grouping, joins and data grain.
Read courses/csharp/guides/csharp-021.md and courses/csharp/lessons/csharp-021.cs. Prerequisites: csharp-020.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-021_solution.cs and
courses/csharp/solutions/csharp-021_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
