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

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Use a record for a stable event schema and serialize explicit safe fields. Stopwatch is appropriate for elapsed duration, but tests should not assert a narrow timing threshold. Keep correlation identity separate from user secrets.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Identify safe fields and the event population.

2. **Guided modification.** Add a stage value without adding raw input content.

3. **Independent construction.** Instrument your import project with submitted, accepted and rejected counts.

4. **Diagnose a defect.** Diagnose a success metric incremented before persistence completes.

5. **Boundary evidence.** Test zero submitted records and choose a no-data rate representation.

6. **Transfer and justify.** Design a latency report that includes percentiles, sample count and measurement boundaries.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. The separate explanation gives an executed reference answer where one has been written and says plainly where none exists yet. Open it only after your own attempt, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Correlation identifiers should not contain credentials or private payloads. High-cardinality dimensions can overwhelm metric systems. Missing observations must not be silently counted as successful operations.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Reproduce Example A (Emit a safe result record) before changing anything, and confirm its observation: The serialized event contains an explicit rejected outcome.
2. Compare Example B (Keep outcome counts consistent) with Example A and name the first line whose behavior differs. Its observation is: The accepted and rejected events account for all five submitted records, and the rejection rate is 0.4.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Correlation identifiers should not contain credentials or private payloads.

## Self-check and next step

Explain Structured event, Correlation identity, Metric without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
