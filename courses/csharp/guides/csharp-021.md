# csharp-021: Grouping, joins and data grain

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-020`

## Learning objectives

Build a report joining unique item metadata to item totals. Then design checks that distinguish one-to-one, one-to-many and many-to-many joins before aggregation.

## Purpose and mental model

Aggregation changes the grain of data. A row-per-event input can become a row-per-category result. State that grain before writing GroupBy so the result keys and totals have a meaning. Joining two sequences can multiply rows when keys are duplicated. This is a modeling issue that appears in LINQ just as it does in SQL.

An inner join drops keys with no partner. A left join needs an explicit absence policy. Before trusting a total after a join, inspect key uniqueness and count the expected matches. A tiny fixture with duplicate keys reveals accidental multiplication far more clearly than a large realistic dataset.

## Vocabulary and concepts

**Grain:** What one row or result item represents.

**Cardinality:** The number of records or matches.

**Join key:** The identity relating two datasets.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`GroupBy(keySelector)` returns groups with Key and enumerable members. `Join` uses one key selector per side. A grouped lookup such as ToLookup preserves all matches, while ToDictionary requires unique keys.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            var rows = new[] { (Kind: "a", Amount: 2), (Kind: "a", Amount: 3), (Kind: "b", Amount: 4) };
            var totals = rows.GroupBy(row => row.Kind).ToDictionary(group => group.Key, group => group.Sum(row => row.Amount));
            Check(totals["a"] == 5 && totals["b"] == 4, "one total per kind");
        }
        Console.WriteLine("csharp-021: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Three event rows become two category totals.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            var left = new[] { (Key: 1, Label: "L") };
            var right = new[] { (Key: 1, Value: "x"), (Key: 1, Value: "y") };
            var joined = left.Join(right, item => item.Key, item => item.Key, (a, b) => a.Label + b.Value).ToArray();
            Check(joined.SequenceEqual(new[] { "Lx", "Ly" }), "two right matches");
        }
        Console.WriteLine("csharp-021: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** One left row becomes two joined rows.

## Exercises

1. **Predict and explain.** State the input and output grain for each example.

2. **Guided modification.** Add a third category and verify total conservation.

3. **Independent construction.** Build a report joining unique item metadata to item totals.

4. **Diagnose a defect.** Diagnose a doubled total caused by duplicate metadata keys.

5. **Boundary evidence.** Test an unmatched key and choose an explicit handling policy.

6. **Transfer and justify.** Design checks that distinguish one-to-one, one-to-many and many-to-many joins before aggregation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Aggregating after an unintended many-to-many join can inflate totals. ToDictionary throws on duplicate keys rather than choosing a winner. Sorting is needed when presentation order is part of the contract.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Grain, Cardinality, Join key without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
