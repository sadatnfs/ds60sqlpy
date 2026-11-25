# csharp-027: Dates, durations and culture-independent data

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-026`

## Learning objectives

Represent instants and durations with DateTimeOffset and format them independently of culture. The central exercise is task 3: Build a duration report using fixed UTC timestamps.

## Purpose and mental model

An instant, a local wall-clock time and a duration are different concepts. DateTimeOffset combines a date-time with an offset, making an instant comparison explicit. A time-zone identifier carries additional historical daylight-saving rules that a fixed offset does not. Do not infer a region from its offset alone.

A duration measures elapsed time; a calendar rule such as next month follows calendar boundaries. Persist machine-readable data using a stable format and parse with an explicit culture. User-facing formatting may intentionally vary by locale. Tests should fix their clock inputs rather than depend on the date or local zone of the machine running them.

## Vocabulary and concepts

**Instant:** A point on the time line.

**Offset:** A displacement from UTC at one observation.

**Duration:** An elapsed interval between instants.

## How to run this lesson

Both examples pass `CultureInfo.InvariantCulture` and use ISO 8601 text with explicit offsets, so the results do not depend on the machine's time zone or language. Example B builds its timestamps from fixed numbers instead of reading the clock, which keeps every run identical.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`DateTimeOffset.Parse` with an explicit round-trip string creates a known instant. `ToUniversalTime` changes its display offset while retaining the instant. Subtraction produces TimeSpan. InvariantCulture avoids environment-dependent machine-data parsing.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** Noon at +02:00 and 10:00 at Z (UTC) name the same moment, because subtracting two hours from noon gives 10:00 UTC. `DateTimeOffset` equality compares the UTC instants, so `a == b` is true. The offsets themselves differ, so the second check passes. `a.EqualsExact(b)` compares offsets too and returns false, and the local clock values, 12:00 and 10:00, differ.

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

**Trace.** `start` is midnight on January 1, 2025, at offset zero. `AddMinutes(90)` returns a new value 90 minutes later; `DateTimeOffset` is immutable. Subtracting gives a `TimeSpan` whose `TotalMinutes` is 90. The round-trip O format writes the full precision and offset, and parsing that text recovers an equal instant, with no culture-specific separators involved.

## Exercises

1. **Predict and explain.** Explain why the two offset timestamps compare equal.

2. **Guided modification.** Change one instant by one minute and predict the comparison.

3. **Independent construction.** Build a duration report using fixed UTC timestamps.

4. **Diagnose a defect.** Diagnose treating an offset as a complete time-zone identity.

5. **Boundary evidence.** Test intervals across midnight and reject an end before its start when the domain forbids it.

6. **Transfer and justify.** Design storage and display policies for appointments in a named time zone.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.

For task 5, an interval from 23:30 to 00:15 the next day still subtracts to 45 minutes, because the values carry their dates. Reversing the operands yields a negative `TimeSpan` rather than an error, so an end-before-start rule must be checked explicitly. For task 2, moving one instant by a minute makes the equality false.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Different offsets, same instant) before changing anything, and confirm its observation: The values denote the same instant despite different offsets.
2. Compare Example B (Measure a fixed duration) with Example A and name the first line whose behavior differs. Its observation is: The elapsed duration is 90 minutes and the timestamp round-trips.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: DateTime kind and unspecified local values can introduce ambiguity.

## Self-check and next step

Explain why `a == b` is true while `a.EqualsExact(b)` is false. State what `end - start` returns when end is earlier than start. For task 6, decide what you store for a recurring appointment in a named time zone and what you compute only when you display it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET guide to dates and times compares `DateTime`, `DateTimeOffset` and `TimeZoneInfo` and explains round-trip formats.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
