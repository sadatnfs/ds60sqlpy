# csharp-032: Composition project: a deterministic import service

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-031`

## Learning objectives

Build a per-item result while preserving the rejected count. Then design an adapter boundary for a file or HTTP source without putting I/O inside the pure aggregation.

## Purpose and mental model

The intermediate project separates a transport representation, validation, a pure aggregation and an asynchronous service boundary. This makes failure location visible. JSON syntax errors belong to decoding; invalid records belong to domain validation; a cancelled operation must not be presented as an empty successful import.

A complete service also owns its dependency lifetime and result shape. The classroom version uses an in-memory JSON payload, avoiding external I/O while preserving the same boundary decisions. A production adapter can load bytes from a file or HTTP response, then call the same pure core. Keep the core deterministic so integration failures do not obscure calculation errors.

## Vocabulary and concepts

**Transport model:** A representation of data crossing a boundary.

**Domain validation:** Checking whether represented data is admissible.

**Service result:** A stable description of completed work.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

An async method can validate cancellation before admitting work and return a record describing accepted totals and rejected counts. Immutable result fields make it easier to store a receipt without later mutation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Import valid and invalid records

Validation remains visible in the result instead of silently converting bad records into ordinary data.

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
            var result = await ImportAsync("[{\"Name\":\"pear\",\"Quantity\":2},{\"Name\":\"\",\"Quantity\":3}]", CancellationToken.None);
            Check(result.Total == 2 && result.Rejected == 1, "validated aggregate");
        }
        Console.WriteLine("csharp-032: passed");
        await Task.CompletedTask;
    }

    public record ImportItem(string Name, int Quantity);
    public record ImportResult(int Total, int Rejected);
    public static async Task<ImportResult> ImportAsync(string json, CancellationToken token) { token.ThrowIfCancellationRequested(); var items = JsonSerializer.Deserialize<ImportItem[]>(json) ?? throw new ArgumentException("array required"); int total = 0, rejected = 0; foreach (var item in items) { token.ThrowIfCancellationRequested(); if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) { rejected++; continue; } total = checked(total + item.Quantity); } await Task.CompletedTask; return new ImportResult(total, rejected); }
}
```

**Observe:** The service returns total 2 and one rejected record.

### Example B: Cancellation is not an empty report

The result category carries meaning beyond a numeric total.

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
            using var source = new CancellationTokenSource(); source.Cancel();
            bool cancelled = false;
            try { await ImportAsync("[]", source.Token); } catch (OperationCanceledException) { cancelled = true; }
            Check(cancelled, "cancelled request preserved");
            Check((await ImportAsync("[]", CancellationToken.None)).Total == 0, "successful empty report");
        }
        Console.WriteLine("csharp-032: passed");
        await Task.CompletedTask;
    }

    public record ImportItem(string Name, int Quantity);
    public record ImportResult(int Total, int Rejected);
    public static async Task<ImportResult> ImportAsync(string json, CancellationToken token) { token.ThrowIfCancellationRequested(); var items = JsonSerializer.Deserialize<ImportItem[]>(json) ?? throw new ArgumentException("array required"); int total = 0, rejected = 0; foreach (var item in items) { token.ThrowIfCancellationRequested(); if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) { rejected++; continue; } total = checked(total + item.Quantity); } await Task.CompletedTask; return new ImportResult(total, rejected); }
}
```

**Observe:** A cancelled request and a successful empty import have different outcomes.

## Exercises

1. **Predict and explain.** Trace syntax, validation and aggregation as separate stages.

2. **Guided modification.** Add a duplicate valid name and document whether total quantity or distinct count is reported.

3. **Independent construction.** Build a per-item result while preserving the rejected count.

4. **Diagnose a defect.** Diagnose catch-all logic returning an empty report after cancellation.

5. **Boundary evidence.** Test malformed JSON, JSON null, an empty list and invalid quantities.

6. **Transfer and justify.** Design an adapter boundary for a file or HTTP source without putting I/O inside the pure aggregation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A transport DTO is not automatically a trusted domain object. Do not merge cancelled, invalid and successfully empty results into one representation. An async signature alone does not make CPU work asynchronous.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Transport model, Domain validation, Service result without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-032: Composition project: a deterministic import service.
Read courses/csharp/guides/csharp-032.md and courses/csharp/lessons/csharp-032.cs. Prerequisites: csharp-031.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-032_solution.cs and
courses/csharp/solutions/csharp-032_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
