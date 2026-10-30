# csharp-040: Domain architecture and dependency direction

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-039`

## Learning objectives

Extract the inventory aggregation into a transport-independent core. Then draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.

## Purpose and mental model

Domain logic expresses the rules that make an operation valid. Transport and storage adapters translate external representations into those rules. If the domain directly opens a database or reads environment variables, its behavior becomes difficult to reproduce. Dependency direction should let outer adapters depend on the core contract while the core remains independent of a specific transport.

Dependency injection is a construction technique, not a requirement to install a container library. Explicit constructors are often enough. Supply clocks, identifiers and repositories where variation matters. Avoid an interface for every trivial value; use abstraction where it separates policy from an unstable or expensive mechanism.

## Vocabulary and concepts

**Domain core:** Rules independent of storage and transport details.

**Adapter:** A translation between an external mechanism and a core contract.

**Dependency direction:** Which layer knows the details of another layer.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A service constructor accepts an interface. A small in-memory implementation supports deterministic tests. A clock abstraction returns a fixed instant in tests while a real adapter would obtain current time.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Identify policy and mechanism in the service.

2. **Guided modification.** Supply a second fixed clock and predict the changed timestamp.

3. **Independent construction.** Extract the inventory aggregation into a transport-independent core.

4. **Diagnose a defect.** Diagnose a domain method reading the system clock internally despite accepting a clock.

5. **Boundary evidence.** Test empty identity and a fixed instant around a date boundary.

6. **Transfer and justify.** Draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Domain core, Adapter, Dependency direction without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
