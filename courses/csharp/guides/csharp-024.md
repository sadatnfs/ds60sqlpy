# csharp-024: Disposable resources and deterministic cleanup

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-023`

## Learning objectives

Write a helper that reads from a caller-owned stream without closing it. Then document ownership and leave-open behavior for a parser that wraps a stream reader.

## Purpose and mental model

Managed memory collection does not mean every resource can wait for garbage collection. Files, sockets and handles need a clear owner that releases them promptly. IDisposable expresses synchronous cleanup. A using declaration or statement arranges Dispose when control leaves the scope, including exceptions.

Ownership is a contract between caller and callee. If a function receives a stream, it should not close a caller-owned stream unless documented. Multiple wrappers can share an underlying resource, so leave-open options matter. Deterministic cleanup prevents resource exhaustion and also makes tests independent: a later operation should not inherit a locked file from an earlier failure.

## Vocabulary and concepts

**Resource owner:** The component responsible for release.

**IDisposable:** A contract for deterministic synchronous cleanup.

**Scope:** The region that bounds a local lifetime.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`using (var resource = ...) { ... }` scopes lifetime. `using var resource = ...` disposes at the end of the containing scope. `await using` supports IAsyncDisposable when cleanup itself is asynchronous.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Dispose on ordinary scope exit

Scope exit is the ownership boundary; no garbage-collector timing is needed.

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
      var resource = new Probe();
      using (resource) { Check(!resource.Closed, "open inside scope"); }
      Check(resource.Closed, "closed after scope");
    }
    Console.WriteLine("csharp-024: passed");
    await Task.CompletedTask;
  }

  public sealed class Probe : IDisposable {
    public bool Closed { get; private set; }
    public void Dispose() { Closed = true; }
  }
}
```

**Observe:** The resource is open inside and closed afterward.

### Example B: Dispose after failure

The same cleanup contract applies to abnormal control flow, which is where manual release is often forgotten.

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
      var resource = new Probe();
      try {
        using (resource) { throw new InvalidOperationException("fixture"); }
      } catch (InvalidOperationException) {
      }
      Check(resource.Closed, "exception still cleans up");
    }
    Console.WriteLine("csharp-024: passed");
    await Task.CompletedTask;
  }

  public sealed class Probe : IDisposable {
    public bool Closed { get; private set; }
    public void Dispose() { Closed = true; }
  }
}
```

**Observe:** The controlled exception still triggers cleanup.

## Exercises

1. **Predict and explain.** Trace the point at which Dispose runs in each example.

2. **Guided modification.** Nest two resources and predict reverse disposal order.

3. **Independent construction.** Write a helper that reads from a caller-owned stream without closing it.

4. **Diagnose a defect.** Diagnose returning a stream from inside a using scope.

5. **Boundary evidence.** Test cleanup after an exception before normal completion.

6. **Transfer and justify.** Document ownership and leave-open behavior for a parser that wraps a stream reader.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Resource owner, IDisposable, Scope without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-024: Disposable resources and deterministic cleanup.
Read courses/csharp/guides/csharp-024.md and courses/csharp/lessons/csharp-024.cs. Prerequisites: csharp-023.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-024_solution.cs and
courses/csharp/solutions/csharp-024_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
