# csharp-048: Capstone: a reviewable .NET data application

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-047`

## Learning objectives

Build the external DomainLab and expose the domain contract through the ApiLab adapter. Then deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.

## Purpose and mental model

The final project combines validated input, a pure domain core, deterministic reporting and explicit operational outcomes. A complete application is more than a successful algorithm: it needs a documented build, input contract, failure policy, resource ownership and evidence that its output remains meaningful after changes.

The classroom reference is the portable kernel, and the DomainLab and ApiLab fixtures provide actual multi-file boundaries. Extend them deliberately rather than pasting an entire server into the single source pad. Review normal, rejected and unknown outcomes separately. Expert practice means being able to explain the limits and diagnose an unfamiliar failure, not claiming that a finite tutorial covers every production circumstance.

## Vocabulary and concepts

**Acceptance criteria:** Observable conditions defining a completed feature.

**Evidence boundary:** The scope actually established by a test or run.

**Maintainability:** The ability to change behavior without losing understandable contracts.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The [DomainLab](../fixtures/DomainLab/README.md) and [ApiLab](../fixtures/ApiLab/README.md) are complete prepared project starting points. Their build and server acceptance are separate from the portable reference.

## Syntax anatomy and execution trace

Compose small functions around explicit record types. Keep parsing, validation, aggregation and presentation separate. Sort output when order is part of the contract; retain rejection evidence alongside accepted totals.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Build a stable valid report

Sorting and aggregation have independent responsibilities and both are observable.

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
            var report = Report(new[] { new Row("b", 2), new Row("a", 3), new Row("b", 4) });
            Check(report.Text == "a=3;b=6" && report.Rejected == 0, "stable report");
        }
        Console.WriteLine("csharp-048: passed");
        await Task.CompletedTask;
    }

    public record Row(string Name, int Quantity);
    public static (string Text, int Rejected) Report(IEnumerable<Row> rows) { var valid = new List<Row>(); int rejected = 0; foreach (var row in rows) { if (string.IsNullOrWhiteSpace(row.Name) || row.Quantity < 0) rejected++; else valid.Add(row); } string text = string.Join(";", valid.GroupBy(row => row.Name).OrderBy(group => group.Key, StringComparer.Ordinal).Select(group => group.Key + "=" + group.Sum(row => row.Quantity).ToString(CultureInfo.InvariantCulture))); return (text, rejected); }
}
```

**Observe:** The sorted report is a=3;b=6.

### Example B: Preserve rejected data accounting

A correct result preserves domain distinctions instead of hiding them behind a plausible total.

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
            var report = Report(new[] { new Row("", 2), new Row("a", -1), new Row("b", 0) });
            Check(report.Text == "b=0" && report.Rejected == 2, "zero differs from rejected");
            Check(Report(Array.Empty<Row>()).Text == "", "empty input");
        }
        Console.WriteLine("csharp-048: passed");
        await Task.CompletedTask;
    }

    public record Row(string Name, int Quantity);
    public static (string Text, int Rejected) Report(IEnumerable<Row> rows) { var valid = new List<Row>(); int rejected = 0; foreach (var row in rows) { if (string.IsNullOrWhiteSpace(row.Name) || row.Quantity < 0) rejected++; else valid.Add(row); } string text = string.Join(";", valid.GroupBy(row => row.Name).OrderBy(group => group.Key, StringComparer.Ordinal).Select(group => group.Key + "=" + group.Sum(row => row.Quantity).ToString(CultureInfo.InvariantCulture))); return (text, rejected); }
}
```

**Observe:** A valid zero remains in the report while two invalid rows are counted.

## Exercises

1. **Predict and explain.** Trace every input to an accepted total or a rejection.

2. **Guided modification.** Add an item and update only independently derived expected output.

3. **Independent construction.** Build the external DomainLab and expose the domain contract through the ApiLab adapter.

4. **Diagnose a defect.** Introduce and diagnose a duplicate-aggregation, nullability or cancellation defect.

5. **Boundary evidence.** Document and test empty, malformed, overflow and repeated-operation boundaries.

6. **Transfer and justify.** Deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Acceptance criteria, Evidence boundary, Maintainability without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-048: Capstone: a reviewable .NET data application.
Read courses/csharp/guides/csharp-048.md and courses/csharp/lessons/csharp-048.cs. Prerequisites: csharp-047.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-048_solution.cs and
courses/csharp/solutions/csharp-048_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
