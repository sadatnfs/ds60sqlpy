# csharp-044: Diagnostics, structured events and operational evidence

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-043`

## Learning objectives

Emit structured events and counts that account for every submitted record. The central exercise is task 3: Instrument your import project with submitted, accepted and rejected counts.

## Purpose and mental model

Diagnostics should explain an operation without leaking its inputs or creating an overwhelming stream of unrelated messages. A structured event has stable fields such as operation identity, stage and outcome. These fields let a reader connect the beginning and end of one operation and distinguish a retry from a different request.

Latency, throughput and failure rate describe different aspects of a service. A low average latency can hide a bad tail. A successful process exit does not imply every record was accepted. Define observable counters from the domain contract, and ensure cancelled or unknown work is not misclassified as success. Deterministic fixtures can verify event structure while production measurements need real workloads.

## Vocabulary and concepts

**Structured event:** A diagnostic record with named stable fields.

**Correlation identity:** A value linking observations of one operation.

**Metric:** An aggregated numerical observation over a defined population.

## How to run this lesson

`Event` is a record declared after `Main`, and the examples serialize it with `JsonSerializer` from `System.Text.Json`. No logger or metrics package is needed: the lesson is about what an event contains and how its counts add up, which the pad can check exactly without timing anything.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

Use a record for a stable event schema and serialize explicit safe fields. Stopwatch is appropriate for elapsed duration, but tests should not assert a narrow timing threshold. Keep correlation identity separate from user secrets.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Emit a safe result record

Named fields retain meaning without depending on a fragile formatted sentence.

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
      var evt = new Event("fixture-1", "validate", "rejected", 2);
      string json = JsonSerializer.Serialize(evt);
      using var parsed = JsonDocument.Parse(json);
      Check(parsed.RootElement.GetProperty("Outcome").GetString() == "rejected",
            "outcome retained");
    }
    Console.WriteLine("csharp-044: passed");
    await Task.CompletedTask;
  }

  public record Event(string OperationId, string Stage, string Outcome,
                      int Count);
}
```

**Observe:** The serialized event contains an explicit rejected outcome.

**Trace.** `new Event("fixture-1", "validate", "rejected", 2)` fills four named fields. `JsonSerializer.Serialize` writes them under their C# names, producing an object with OperationId, Stage, Outcome and Count. Parsing that text and reading the Outcome property returns rejected. The default serializer keeps Pascal case, so `GetProperty("outcome")` would throw `KeyNotFoundException`. Readers of the event must use the exact field names it was written with.

### Example B: Keep outcome counts consistent

The counts come from the emitted events, so a record that was never classified would make the first check fail. The denominator is stated explicitly; changing it changes the metric meaning.

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
      var accepted = new Event("op-7", "save", "accepted", 3);
      var rejected = new Event("op-7", "save", "rejected", 2);
      Event[] events = { accepted, rejected };
      int submitted = 5;
      Check(events.Sum(evt => evt.Count) == submitted, "accounted input");
      Check((double)rejected.Count / submitted == 0.4, "rejection rate");
    }
    Console.WriteLine("csharp-044: passed");
    await Task.CompletedTask;
  }

  public record Event(string OperationId, string Stage, string Outcome,
                      int Count);
}
```

**Observe:** The accepted and rejected events account for all five submitted records, and the rejection rate is 0.4.

**Trace.** Two events share operation op-7: accepted carries 3 and rejected carries 2. `events.Sum` adds the counts to 5, matching `submitted`, so every input is accounted for. The rate casts 2 to `double` before dividing by 5, giving exactly the 0.4 the check compares against. Without the cast, `2 / 5` is integer division and yields 0.

## Exercises

1. **Predict and explain.** Identify safe fields and the event population.

2. **Guided modification.** Add a stage value without adding raw input content.

3. **Independent construction.** Instrument your import project with submitted, accepted and rejected counts.

4. **Diagnose a defect.** Diagnose a success metric incremented before persistence completes.

5. **Boundary evidence.** Test zero submitted records and choose a no-data rate representation.

6. **Transfer and justify.** Design a latency report that includes percentiles, sample count and measurement boundaries.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Correlation identifiers should not contain credentials or private payloads. High-cardinality dimensions can overwhelm metric systems. Missing observations must not be silently counted as successful operations.

For task 4, a counter incremented before the save completes reports success for writes that then fail; move it after the awaited persistence call. For task 5, zero submitted records gives NaN from `0.0 / 0` and `DivideByZeroException` from integer `0 / 0`, so choose an explicit no-data value instead of either one.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Emit a safe result record) before changing anything, and confirm its observation: The serialized event contains an explicit rejected outcome.
2. Compare Example B (Keep outcome counts consistent) with Example A and name the first line whose behavior differs. Its observation is: The accepted and rejected events account for all five submitted records, and the rejection rate is 0.4.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Correlation identifiers should not contain credentials or private payloads.

## Self-check and next step

List which `Event` fields are safe to log and which input content must never appear. Explain why the counts must sum to `submitted`. For task 6, describe a latency report with p50, p95 and p99, the number of samples behind each, and where the stopwatch starts and stops.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `System.Text.Json` serialization articles and the .NET diagnostics overview cover event shapes, naming and measurement.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-044: Diagnostics, structured events and operational evidence.
Read courses/csharp/guides/csharp-044.md and courses/csharp/lessons/csharp-044.cs. Prerequisites: csharp-043.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-044_solution.cs and
courses/csharp/solutions/csharp-044_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
