# csharp-040: Domain architecture and dependency direction

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-039`

## Learning objectives

Separate a domain core from its adapters so validation and time are testable without infrastructure. The central exercise is task 3: Extract the inventory aggregation into a transport-independent core.

## Purpose and mental model

Domain logic expresses the rules that make an operation valid. Transport and storage adapters translate external representations into those rules. If the domain directly opens a database or reads environment variables, its behavior becomes difficult to reproduce. Dependency direction should let outer adapters depend on the core contract while the core remains independent of a specific transport.

Dependency injection is a construction technique, not a requirement to install a container library. Explicit constructors are often enough. Supply clocks, identifiers and repositories where variation matters. Avoid an interface for every trivial value; use abstraction where it separates policy from an unstable or expensive mechanism.

## Vocabulary and concepts

**Domain core:** Rules independent of storage and transport details.

**Adapter:** A translation between an external mechanism and a core contract.

**Dependency direction:** Which layer knows the details of another layer.

## How to run this lesson

`IClock`, `FixedClock` and `StampService` are declared after `Main`; the service takes its clock through a primary constructor. No real clock adapter appears, because the lesson concerns dependency direction: the domain names the capability it needs, and the test supplies a fixed answer. `CultureInfo` comes from `System.Globalization`, already imported.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

A service constructor accepts an interface. A small in-memory implementation supports deterministic tests. A clock abstraction returns a fixed instant in tests while a real adapter would obtain current time.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Inject a deterministic clock

The domain behavior does not depend on the machine clock during the test.

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
      var service = new StampService(new FixedClock(
          new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero)));
      Check(
          service.Stamp("a").StartsWith("2025-01-01", StringComparison.Ordinal),
          "fixed time");
    }
    Console.WriteLine("csharp-040: passed");
    await Task.CompletedTask;
  }

  public interface IClock {
    DateTimeOffset Now { get; }
  }
  public sealed record FixedClock(DateTimeOffset Now) : IClock;
  public sealed class StampService(IClock clock) {
    public string Stamp(string id) {
      if (string.IsNullOrWhiteSpace(id))
        throw new ArgumentException("identity required");
      return clock.Now.ToString("O", CultureInfo.InvariantCulture) + ":" + id;
    }
  }
}
```

**Observe:** The result uses the supplied instant.

**Trace.** `FixedClock` wraps midnight on January 1, 2025, at offset zero. `Stamp("a")` first validates the identity, then formats `clock.Now` with the round-trip O format and appends a colon and the identity, producing 2025-01-01T00:00:00.0000000+00:00:a. The check reads only the leading date, which cannot vary between runs because no machine clock is consulted.

### Example B: Preserve a core validation rule

Dependency variation should not weaken the invariant owned by the domain.

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
      var service = new StampService(new FixedClock(DateTimeOffset.UnixEpoch));
      bool rejected = false;
      try {
        service.Stamp("");
      } catch (ArgumentException) {
        rejected = true;
      }
      Check(rejected, "domain rejects empty identity");
    }
    Console.WriteLine("csharp-040: passed");
    await Task.CompletedTask;
  }

  public interface IClock {
    DateTimeOffset Now { get; }
  }
  public sealed record FixedClock(DateTimeOffset Now) : IClock;
  public sealed class StampService(IClock clock) {
    public string Stamp(string id) {
      if (string.IsNullOrWhiteSpace(id))
        throw new ArgumentException("identity required");
      return clock.Now.ToString("O", CultureInfo.InvariantCulture) + ":" + id;
    }
  }
}
```

**Observe:** A different clock does not bypass identity validation.

**Trace.** The clock now returns `DateTimeOffset.UnixEpoch`, January 1, 1970, but `Stamp("")` never reaches it. `string.IsNullOrWhiteSpace` rejects the empty text and the method throws `ArgumentException` with the message identity required. A string of spaces fails the same test. Swapping clocks changed the data the service could see, not the rule it enforces.

## Exercises

1. **Predict and explain.** Identify policy and mechanism in the service.

2. **Guided modification.** Supply a second fixed clock and predict the changed timestamp.

3. **Independent construction.** Extract the inventory aggregation into a transport-independent core.

4. **Diagnose a defect.** Diagnose a domain method reading the system clock internally despite accepting a clock.

5. **Boundary evidence.** Test empty identity and a fixed instant around a date boundary.

6. **Transfer and justify.** Draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.

For task 4, a method that calls `DateTimeOffset.UtcNow` internally while accepting an `IClock` makes the test pass today and fail at midnight, so search for direct clock calls. For task 5, the instant 23:30 at offset minus five formats as 2024-12-31 even though the same moment is 04:30 on January 1 in UTC; decide which date the domain means.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Inject a deterministic clock) before changing anything, and confirm its observation: The result uses the supplied instant.
2. Compare Example B (Preserve a core validation rule) with Example A and name the first line whose behavior differs. Its observation is: A different clock does not bypass identity validation.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A dependency container can conceal construction errors if overused.

## Self-check and next step

Name the policy and the mechanism in `StampService`, and say which file would change if the stamp format changed. Explain why the second example needs no particular clock value. For task 6, draw the arrows between the command-line adapter, the HTTP adapter and the domain library, and confirm no arrow points out of the domain.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide's articles on interfaces and primary constructors explain how the service receives its clock without depending on an implementation.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-040: Domain architecture and dependency direction.
Read courses/csharp/guides/csharp-040.md and courses/csharp/lessons/csharp-040.cs. Prerequisites: csharp-039.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-040_solution.cs and
courses/csharp/solutions/csharp-040_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
