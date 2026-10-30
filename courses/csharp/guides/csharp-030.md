# csharp-030: Cooperative cancellation and bounded waiting

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-029`

## Learning objectives

Write an operation that stops cooperatively and preserves already committed work. Then design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.

## Purpose and mental model

Cancellation is a request for cooperation. A CancellationTokenSource owns the request; its token lets operations observe it. An operation that never checks or passes the token can continue after cancellation is requested. A timeout on the caller waiting is also distinct from termination of the underlying work.

Correct ownership includes awaiting or otherwise accounting for admitted work after a timeout. Do not retry a state-changing operation merely because the result is unknown. The first operation may still complete. Use operation identity and recovery evidence for such systems. Here, a TaskCompletionSource establishes exact states without guessing how long a background task takes.

## Vocabulary and concepts

**Cancellation token:** A cooperative notification of requested cancellation.

**Wait cancellation:** Stopping observation without proving work stopped.

**Unknown result:** An operation whose final effect has not yet been observed.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`ThrowIfCancellationRequested` reports acknowledged cancellation. `WaitAsync(token)` cancels the wait without necessarily canceling the source task. TaskCompletionSource with RunContinuationsAsynchronously avoids executing arbitrary continuations inline inside a signal setter.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Observe a requested cancellation

Calling Cancel changes request state; the explicit observation is what changes the operation control flow.

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
      bool observed = false;
      try {
        source.Token.ThrowIfCancellationRequested();
      } catch (OperationCanceledException) {
        observed = true;
      }
      Check(observed, "cooperative observation");
    }
    Console.WriteLine("csharp-030: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The token check acknowledges cancellation.

### Example B: Cancel waiting while work remains live

This deterministic distinction prevents treating an interrupted observer as proof that an operation never happened.

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
      var completion = new TaskCompletionSource<int>(
          TaskCreationOptions.RunContinuationsAsynchronously);
      using var source = new CancellationTokenSource();
      source.Cancel();
      bool cancelled = false;
      try {
        await completion.Task.WaitAsync(source.Token);
      } catch (OperationCanceledException) {
        cancelled = true;
      }
      Check(cancelled && !completion.Task.IsCompleted, "only the wait ended");
      completion.SetResult(9);
      Check(await completion.Task == 9, "underlying result still arrives");
    }
    Console.WriteLine("csharp-030: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The wait cancels, then the original task later completes with 9.

## Exercises

1. **Predict and explain.** Identify the request, observation and completion events.

2. **Guided modification.** Pass a token through a helper and check it before a state change.

3. **Independent construction.** Write an operation that stops cooperatively and preserves already committed work.

4. **Diagnose a defect.** Diagnose automatically replaying a write after its waiter times out.

5. **Boundary evidence.** Test cancellation requested before start and after successful completion.

6. **Transfer and justify.** Design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A catch for OperationCanceledException should match the intended cancellation policy. Cancelling a waiter does not dispose all resources owned by the operation. Retain and observe tasks that may still complete.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Cancellation token, Wait cancellation, Unknown result without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-030: Cooperative cancellation and bounded waiting.
Read courses/csharp/guides/csharp-030.md and courses/csharp/lessons/csharp-030.cs. Prerequisites: csharp-029.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-030_solution.cs and
courses/csharp/solutions/csharp-030_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
