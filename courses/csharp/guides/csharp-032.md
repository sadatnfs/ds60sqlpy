# csharp-032: Composition project: a deterministic import service

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-031`

## Learning objectives

Build a deterministic, cancellable import service that keeps per-item results and rejection counts. The central exercise is task 3: Build a per-item result while preserving the rejected count.

## Purpose and mental model

The intermediate project separates a transport representation, validation, a pure aggregation and an asynchronous service boundary. This makes failure location visible. JSON syntax errors belong to decoding; invalid records belong to domain validation; a cancelled operation must not be presented as an empty successful import.

A complete service also owns its dependency lifetime and result shape. The classroom version uses an in-memory JSON payload, avoiding external I/O while preserving the same boundary decisions. A production adapter can load bytes from a file or HTTP response, then call the same pure core. Keep the core deterministic so integration failures do not obscure calculation errors.

## Vocabulary and concepts

**Transport model:** A representation of data crossing a boundary.

**Domain validation:** Checking whether represented data is admissible.

**Service result:** A stable description of completed work.

## How to run this lesson

`ImportAsync` is a single-line helper after `Main` that combines earlier lessons: JSON decoding, validation, checked accumulation and cancellation checks. It awaits only `Task.CompletedTask`, so it finishes synchronously; the async signature is there so that a real source could be awaited later without changing callers.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

An async method can validate cancellation before admitting work and return a record describing accepted totals and rejected counts. Immutable result fields make it easier to store a receipt without later mutation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var result = await ImportAsync(
          "[{\"Name\":\"pear\",\"Quantity\":2},{\"Name\":\"\",\"Quantity\":3}]",
          CancellationToken.None);
      Check(result.Total == 2 && result.Rejected == 1, "validated aggregate");
    }
    Console.WriteLine("csharp-032: passed");
    await Task.CompletedTask;
  }

  public record ImportItem(string Name, int Quantity);
  public record ImportResult(int Total, int Rejected);
  public static async Task<ImportResult> ImportAsync(string json,
                                                     CancellationToken token) {
    token.ThrowIfCancellationRequested();
    var items = JsonSerializer.Deserialize<ImportItem[]>(json) ??
                throw new ArgumentException("array required");
    int total = 0, rejected = 0;
    foreach (var item in items) {
      token.ThrowIfCancellationRequested();
      if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
        rejected++;
        continue;
      }
      total = checked(total + item.Quantity);
    }
    await Task.CompletedTask;
    return new ImportResult(total, rejected);
  }
}
```

**Observe:** The service returns total 2 and one rejected record.

**Trace.** The token is not cancelled, so the first check passes. The text decodes into two `ImportItem` records. The first, pear with 2, passes validation and the total becomes 2. The second has a blank name, so `rejected` becomes 1 and its quantity is skipped. The result record holds total 2 and one rejection.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      using var source = new CancellationTokenSource();
      source.Cancel();
      bool cancelled = false;
      try {
        await ImportAsync("[]", source.Token);
      } catch (OperationCanceledException) {
        cancelled = true;
      }
      Check(cancelled, "cancelled request preserved");
      Check((await ImportAsync("[]", CancellationToken.None)).Total == 0,
            "successful empty report");
    }
    Console.WriteLine("csharp-032: passed");
    await Task.CompletedTask;
  }

  public record ImportItem(string Name, int Quantity);
  public record ImportResult(int Total, int Rejected);
  public static async Task<ImportResult> ImportAsync(string json,
                                                     CancellationToken token) {
    token.ThrowIfCancellationRequested();
    var items = JsonSerializer.Deserialize<ImportItem[]>(json) ??
                throw new ArgumentException("array required");
    int total = 0, rejected = 0;
    foreach (var item in items) {
      token.ThrowIfCancellationRequested();
      if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
        rejected++;
        continue;
      }
      total = checked(total + item.Quantity);
    }
    await Task.CompletedTask;
    return new ImportResult(total, rejected);
  }
}
```

**Observe:** A cancelled request and a successful empty import have different outcomes.

**Trace.** With a cancelled token, `ThrowIfCancellationRequested` throws before the JSON is even read, and the catch records cancellation. The second call uses `CancellationToken.None` and the text of an empty array, which decodes to zero items, so the method returns total 0 with no rejections. Cancelled and empty are different outcomes with different evidence.

## Exercises

1. **Predict and explain.** Trace syntax, validation and aggregation as separate stages.

2. **Guided modification.** Add a duplicate valid name and document whether total quantity or distinct count is reported.

3. **Independent construction.** Build a per-item result while preserving the rejected count.

4. **Diagnose a defect.** Diagnose catch-all logic returning an empty report after cancellation.

5. **Boundary evidence.** Test malformed JSON, JSON null, an empty list and invalid quantities.

6. **Transfer and justify.** Design an adapter boundary for a file or HTTP source without putting I/O inside the pure aggregation.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A transport DTO is not automatically a trusted domain object. Do not merge cancelled, invalid and successfully empty results into one representation. An async signature alone does not make CPU work asynchronous.

For task 5, the literal null decodes to a null array, so the helper throws `ArgumentException` with the message array required, while malformed text throws `JsonException` from the decoder. An item without a Quantity key decodes as 0 and is accepted, which is a contract decision to document rather than an accident.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Import valid and invalid records) before changing anything, and confirm its observation: The service returns total 2 and one rejected record.
2. Compare Example B (Cancellation is not an empty report) with Example A and name the first line whose behavior differs. Its observation is: A cancelled request and a successful empty import have different outcomes.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A transport DTO is not automatically a trusted domain object.

## Self-check and next step

Name the stage, decoding, validation or aggregation, that handles each of the two items in Example A. Explain why catching every exception and returning total 0 would hide cancellation. For task 6, describe the adapter that reads a file and the pure function it hands the text to.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# documentation's task-based asynchronous programming pages and the `System.Text.Json` guide cover the pieces this project combines.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
