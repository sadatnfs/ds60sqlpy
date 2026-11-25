# csharp-024: Disposable resources and deterministic cleanup

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-023`

## Learning objectives

Release disposable resources deterministically with using, including when an exception occurs. The central exercise is task 3: Write a helper that reads from a caller-owned stream without closing it.

## Purpose and mental model

Managed memory collection does not mean every resource can wait for garbage collection. Files, sockets and handles need a clear owner that releases them promptly. IDisposable expresses synchronous cleanup. A using declaration or statement arranges Dispose when control leaves the scope, including exceptions.

Ownership is a contract between caller and callee. If a function receives a stream, it should not close a caller-owned stream unless documented. Multiple wrappers can share an underlying resource, so leave-open options matter. Deterministic cleanup prevents resource exhaustion and also makes tests independent: a later operation should not inherit a locked file from an earlier failure.

## Vocabulary and concepts

**Resource owner:** The component responsible for release.

**IDisposable:** A contract for deterministic synchronous cleanup.

**Scope:** The region that bounds a local lifetime.

## How to run this lesson

`Probe` records disposal in its `Closed` property, which is how both examples observe cleanup without real files. For task 4, a method that returns a `MemoryStream` from inside `using var` hands back a disposed stream: the first `ReadByte` call throws `ObjectDisposedException`, cannot access a closed stream.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`using (var resource = ...) { ... }` scopes lifetime. `using var resource = ...` disposes at the end of the containing scope. `await using` supports IAsyncDisposable when cleanup itself is asynchronous.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `resource` is created outside the `using` statement, so the variable outlives the block. Inside the block, `Closed` is still false and the first check passes. Leaving the block calls `Dispose`, which sets Closed to true, and the second check confirms it. The scope boundary, not the garbage collector, decided when cleanup happened.

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

**Trace.** Inside the `using` block, an `InvalidOperationException` is thrown. Before control reaches the outer catch, the compiler-generated `finally` calls `Dispose` on the probe. The catch swallows the expected exception, and the check finds Closed true. Cleanup ran on the failure path as well as on the normal one, with no manual `Dispose` call.

## Exercises

1. **Predict and explain.** Trace the point at which Dispose runs in each example.

2. **Guided modification.** Nest two resources and predict reverse disposal order.

3. **Independent construction.** Write a helper that reads from a caller-owned stream without closing it.

4. **Diagnose a defect.** Diagnose returning a stream from inside a using scope.

5. **Boundary evidence.** Test cleanup after an exception before normal completion.

6. **Transfer and justify.** Document ownership and leave-open behavior for a parser that wraps a stream reader.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.

For task 2, two nested `using` statements dispose in reverse order: inner first, then outer, so an object is never cleaned up before the one that depends on it. For task 3, a helper that reads a caller-owned stream must not dispose it; when it wraps a `StreamReader`, pass `leaveOpen: true` so the reader leaves the stream open.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Dispose on ordinary scope exit) before changing anything, and confirm its observation: The resource is open inside and closed afterward.
2. Compare Example B (Dispose after failure) with Example A and name the first line whose behavior differs. Its observation is: The controlled exception still triggers cleanup.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Dispose does not automatically make an object safe for concurrent callers.

## Self-check and next step

State exactly when `Dispose` runs in each example and what triggers it. Predict the disposal order for outer and inner probes. For task 6, document who owns the stream given to your parser, whether the parser closes it, and what a caller may do with it afterward.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `using` statement article and the guide to implementing a `Dispose` method describe scoped cleanup and `IAsyncDisposable`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
