# csharp-027: Dates, durations and culture-independent data

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-026`

## Learning objectives

Build a duration report using fixed UTC timestamps. Then design storage and display policies for appointments in a named time zone.

## Purpose and mental model

An instant, a local wall-clock time and a duration are different concepts. DateTimeOffset combines a date-time with an offset, making an instant comparison explicit. A time-zone identifier carries additional historical daylight-saving rules that a fixed offset does not. Do not infer a region from its offset alone.

A duration measures elapsed time; a calendar rule such as next month follows calendar boundaries. Persist machine-readable data using a stable format and parse with an explicit culture. User-facing formatting may intentionally vary by locale. Tests should fix their clock inputs rather than depend on the date or local zone of the machine running them.

## Vocabulary and concepts

**Instant:** A point on the time line.

**Offset:** A displacement from UTC at one observation.

**Duration:** An elapsed interval between instants.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`DateTimeOffset.Parse` with an explicit round-trip string creates a known instant. `ToUniversalTime` changes its display offset while retaining the instant. Subtraction produces TimeSpan. InvariantCulture avoids environment-dependent machine-data parsing.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Different offsets, same instant

Comparing wall-clock components would miss the offset information.

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
      var a = DateTimeOffset.Parse("2025-01-01T12:00:00+02:00",
                                   CultureInfo.InvariantCulture);
      var b = DateTimeOffset.Parse("2025-01-01T10:00:00Z",
                                   CultureInfo.InvariantCulture);
      Check(a == b, "same instant");
      Check(a.Offset != b.Offset, "different representations");
    }
    Console.WriteLine("csharp-027: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The values denote the same instant despite different offsets.

### Example B: Measure a fixed duration

A fixed fixture keeps evidence independent of the host clock and locale.

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
      var start = new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero);
      var end = start.AddMinutes(90);
      Check((end - start).TotalMinutes == 90, "elapsed duration");
      string encoded = start.ToString("O", CultureInfo.InvariantCulture);
      Check(DateTimeOffset.Parse(encoded, CultureInfo.InvariantCulture) ==
                start,
            "round-trip format");
    }
    Console.WriteLine("csharp-027: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The elapsed duration is 90 minutes and the timestamp round-trips.

## Exercises

1. **Predict and explain.** Explain why the two offset timestamps compare equal.

2. **Guided modification.** Change one instant by one minute and predict the comparison.

3. **Independent construction.** Build a duration report using fixed UTC timestamps.

4. **Diagnose a defect.** Diagnose treating an offset as a complete time-zone identity.

5. **Boundary evidence.** Test intervals across midnight and reject an end before its start when the domain forbids it.

6. **Transfer and justify.** Design storage and display policies for appointments in a named time zone.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Instant, Offset, Duration without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-027: Dates, durations and culture-independent data.
Read courses/csharp/guides/csharp-027.md and courses/csharp/lessons/csharp-027.cs. Prerequisites: csharp-026.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-027_solution.cs and
courses/csharp/solutions/csharp-027_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
