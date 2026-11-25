# csharp-048: Capstone: a reviewable .NET data application

## Level and prerequisites

Advanced, approximately 180 minutes. Prerequisites: `csharp-047`

## Learning objectives

Build, test and review a complete .NET data application across a domain library and an API adapter. The central exercise is task 3: Build the external DomainLab and expose the domain contract through the ApiLab adapter.

## Purpose and mental model

The final project combines validated input, a pure domain core, deterministic reporting and explicit operational outcomes. A complete application is more than a successful algorithm: it needs a documented build, input contract, failure policy, resource ownership and evidence that its output remains meaningful after changes.

The classroom reference is the portable kernel, and the DomainLab and ApiLab fixtures provide actual multi-file boundaries. Extend them deliberately rather than pasting an entire server into the single source pad. Review normal, rejected and unknown outcomes separately. Expert practice means being able to explain the limits and diagnose an unfamiliar failure, not claiming that a finite tutorial covers every production circumstance.

## Vocabulary and concepts

**Acceptance criteria:** Observable conditions defining a completed feature.

**Evidence boundary:** The scope actually established by a test or run.

**Maintainability:** The ability to change behavior without losing understandable contracts.

## How to run this lesson

`Row` and `Report` sit after `Main`, and the pad runs only this reference kernel. The note below links to DomainLab and ApiLab, the prepared projects where the capstone grows into a class library and an HTTP adapter; their builds and server checks are separate steps with their own requirements.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The [DomainLab](../fixtures/DomainLab/README.md) and [ApiLab](../fixtures/ApiLab/README.md) are complete prepared project starting points. Their build and server acceptance are separate from the portable reference.

## Syntax anatomy and execution trace

Compose small functions around explicit record types. Keep parsing, validation, aggregation and presentation separate. Sort output when order is part of the contract; retain rejection evidence alongside accepted totals.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var report =
          Report(new[] { new Row("b", 2), new Row("a", 3), new Row("b", 4) });
      Check(report.Text == "a=3;b=6" && report.Rejected == 0, "stable report");
    }
    Console.WriteLine("csharp-048: passed");
    await Task.CompletedTask;
  }

  public record Row(string Name, int Quantity);
  public static (string Text, int Rejected) Report(IEnumerable<Row> rows) {
    var valid = new List<Row>();
    int rejected = 0;
    foreach (var row in rows) {
      if (string.IsNullOrWhiteSpace(row.Name) || row.Quantity < 0)
        rejected++;
      else
        valid.Add(row);
    }
    string text = string.Join(
        ";", valid.GroupBy(row => row.Name)
                 .OrderBy(group => group.Key, StringComparer.Ordinal)
                 .Select(group => group.Key + "=" +
                                  group.Sum(row => row.Quantity)
                                      .ToString(CultureInfo.InvariantCulture)));
    return (text, rejected);
  }
}
```

**Observe:** The sorted report is a=3;b=6.

**Trace.** All three rows pass validation. `GroupBy` collects b with 2 and 4 and a with 3. `OrderBy` with `StringComparer.Ordinal` puts a before b, and each group's sum is formatted with the invariant culture, giving a=3 and b=6. `string.Join` writes a=3;b=6, and `Rejected` stays 0 because no row failed either validation test.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var report =
          Report(new[] { new Row("", 2), new Row("a", -1), new Row("b", 0) });
      Check(report.Text == "b=0" && report.Rejected == 2,
            "zero differs from rejected");
      Check(Report(Array.Empty<Row>()).Text == "", "empty input");
    }
    Console.WriteLine("csharp-048: passed");
    await Task.CompletedTask;
  }

  public record Row(string Name, int Quantity);
  public static (string Text, int Rejected) Report(IEnumerable<Row> rows) {
    var valid = new List<Row>();
    int rejected = 0;
    foreach (var row in rows) {
      if (string.IsNullOrWhiteSpace(row.Name) || row.Quantity < 0)
        rejected++;
      else
        valid.Add(row);
    }
    string text = string.Join(
        ";", valid.GroupBy(row => row.Name)
                 .OrderBy(group => group.Key, StringComparer.Ordinal)
                 .Select(group => group.Key + "=" +
                                  group.Sum(row => row.Quantity)
                                      .ToString(CultureInfo.InvariantCulture)));
    return (text, rejected);
  }
}
```

**Observe:** A valid zero remains in the report while two invalid rows are counted.

**Trace.** The blank name and the -1 quantity each add one to `rejected`. The row b with 0 passes, since only negative quantities fail, so the report text is b=0 and `Rejected` is 2. An empty sequence never enters the loop, so `string.Join` over no groups returns the empty string and the count stays 0.

## Exercises

1. **Predict and explain.** Trace every input to an accepted total or a rejection.

2. **Guided modification.** Add an item and update only independently derived expected output.

3. **Independent construction.** Build the external DomainLab and expose the domain contract through the ApiLab adapter.

4. **Diagnose a defect.** Introduce and diagnose a duplicate-aggregation, nullability or cancellation defect.

5. **Boundary evidence.** Document and test empty, malformed, overflow and repeated-operation boundaries.

6. **Transfer and justify.** Deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.

For task 5, ordinal ordering puts capitals first: rows named B, a and A report as A=3;B=1;a=2, because the grouping and sort are case-sensitive. Two quantities of a whose sum exceeds `int.MaxValue` make `Sum` throw `OverflowException` instead of wrapping. For task 4, note that a name of spaces counts as rejected.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Build a stable valid report) before changing anything, and confirm its observation: The sorted report is a=3;b=6.
2. Compare Example B (Preserve rejected data accounting) with Example A and name the first line whose behavior differs. Its observation is: A valid zero remains in the report while two invalid rows are counted.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Do not equate a kernel assertion with API, persistence or deployment acceptance.

## Self-check and next step

Account for every input row in both examples as accepted into a total or counted as rejected. Explain why b=0 and a rejected row are different outcomes. For task 6, check that your README states the build commands, each failure policy, how the tests are run, and what the application deliberately does not support.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide's LINQ articles describe grouping, ordering with an explicit comparer, and the aggregation operators used in the report.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
