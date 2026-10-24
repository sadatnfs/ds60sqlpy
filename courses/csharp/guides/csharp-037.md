# csharp-037: Algorithmic complexity and measured performance

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-036`

## Learning objectives

Compare repeated list scans with one built index while preserving equality policy. Then write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.

## Purpose and mental model

Performance begins with an explicit workload and cost model. A nested search can perform quadratically many comparisons, while an indexed lookup may trade memory for near-constant expected lookup cost. Big-O describes growth, not an exact elapsed time or a universal ranking. Constant factors, data layout and input size matter.

Measure correctness separately from speed. A benchmark that computes a different result is irrelevant. Warmup, allocation, runtime optimization and background load can distort tiny timings. The classroom counts deterministic operations to explain growth; a prepared external benchmark project is the right place for statistically meaningful elapsed-time comparisons.

## Vocabulary and concepts

**Complexity:** How a resource requirement grows with input size.

**Cost model:** The operations or resources being counted.

**Benchmark:** A controlled measurement of implementation behavior.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

HashSet membership can avoid repeated linear scans. Distinct and grouping have equality-policy assumptions. Count comparisons in a fixture instead of asserting a fragile timing threshold.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Count a linear search

The deterministic count illustrates the algorithm independently of machine speed.

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
            int[] values = { 2, 4, 6, 8 };
            int comparisons = 0;
            bool found = false;
            foreach (int value in values) { comparisons++; if (value == 8) { found = true; break; } }
            Check(found && comparisons == 4, "last-element linear search");
        }
        Console.WriteLine("csharp-037: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Finding the last element needs four comparisons.

### Example B: Trade memory for repeated membership

Building and retaining the index has a cost that should be amortized across enough queries.

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
            var index = new HashSet<int>(new[] { 2, 4, 6, 8 });
            Check(index.Contains(8) && !index.Contains(9), "indexed membership");
            Check(index.Count == 4, "index has stored identities");
        }
        Console.WriteLine("csharp-037: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The index answers membership while storing four identities.

## Exercises

1. **Predict and explain.** Count comparisons for first, last and absent targets.

2. **Guided modification.** Double the input size and predict worst-case linear comparisons.

3. **Independent construction.** Compare repeated list scans with one built index while preserving equality policy.

4. **Diagnose a defect.** Diagnose a benchmark that excludes index construction from a one-shot workload.

5. **Boundary evidence.** Test duplicate inputs and empty queries.

6. **Transfer and justify.** Write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Complexity, Cost model, Benchmark without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-037: Algorithmic complexity and measured performance.
Read courses/csharp/guides/csharp-037.md and courses/csharp/lessons/csharp-037.cs. Prerequisites: csharp-036.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-037_solution.cs and
courses/csharp/solutions/csharp-037_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
