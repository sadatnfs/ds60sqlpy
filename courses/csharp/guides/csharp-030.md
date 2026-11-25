# csharp-030: Cooperative cancellation and bounded waiting

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-029`

## Learning objectives

Cancel work cooperatively with CancellationToken while keeping already committed results. The central exercise is task 3: Write an operation that stops cooperatively and preserves already committed work.

## Purpose and mental model

Cancellation is a request for cooperation. A CancellationTokenSource owns the request; its token lets operations observe it. An operation that never checks or passes the token can continue after cancellation is requested. A timeout on the caller waiting is also distinct from termination of the underlying work.

Correct ownership includes awaiting or otherwise accounting for admitted work after a timeout. Do not retry a state-changing operation merely because the result is unknown. The first operation may still complete. Use operation identity and recovery evidence for such systems. Here, a TaskCompletionSource establishes exact states without guessing how long a background task takes.

## Vocabulary and concepts

**Cancellation token:** A cooperative notification of requested cancellation.

**Wait cancellation:** Stopping observation without proving work stopped.

**Unknown result:** An operation whose final effect has not yet been observed.

## How to run this lesson

Both examples cancel their token before starting, so no timing is involved. Example B's wait ends with `TaskCanceledException`, which derives from `OperationCanceledException`, so the catch handles it. The `TaskCompletionSource` is created with `RunContinuationsAsynchronously`, so setting its result never runs awaiting code inline.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`ThrowIfCancellationRequested` reports acknowledged cancellation. `WaitAsync(token)` cancels the wait without necessarily canceling the source task. TaskCompletionSource with RunContinuationsAsynchronously avoids executing arbitrary continuations inline inside a signal setter.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `source` is created and immediately cancelled, which sets a flag on its token. Nothing stops on its own: cancellation is a request. `ThrowIfCancellationRequested` reads the flag, finds it set and throws `OperationCanceledException`. The catch sets `observed`. The operation changed course only at the point where it checked, so code before that check would already have run.

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

**Trace.** `completion.Task` is pending. `WaitAsync(source.Token)` wraps it in a wait that can be cancelled; the token is already cancelled, so the wait throws and `cancelled` becomes true while the underlying task is still incomplete. `SetResult(9)` then completes the original, and awaiting it directly returns 9. Cancelling a wait did not cancel the work.

## Exercises

1. **Predict and explain.** Identify the request, observation and completion events.

2. **Guided modification.** Pass a token through a helper and check it before a state change.

3. **Independent construction.** Write an operation that stops cooperatively and preserves already committed work.

4. **Diagnose a defect.** Diagnose automatically replaying a write after its waiter times out.

5. **Boundary evidence.** Test cancellation requested before start and after successful completion.

6. **Transfer and justify.** Design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A catch for OperationCanceledException should match the intended cancellation policy. Cancelling a waiter does not dispose all resources owned by the operation. Retain and observe tasks that may still complete.

For task 5, `Task.FromResult(5).WaitAsync(cancelledToken)` returns 5: a task that already completed wins over a cancelled token. Task 4's automatic replay after a timed-out wait is the dangerous wrong version, because the first write may still finish and the replay would apply it twice.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe a requested cancellation) before changing anything, and confirm its observation: The token check acknowledges cancellation.
2. Compare Example B (Cancel waiting while work remains live) with Example A and name the first line whose behavior differs. Its observation is: The wait cancels, then the original task later completes with 9.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A catch for OperationCanceledException should match the intended cancellation policy.

## Self-check and next step

Identify where Example B requests cancellation, where it observes it and where the work completes. Explain why `WaitAsync` cannot stop the operation it waits on. For task 6, describe the fields of a receipt that tells the caller whether work was confirmed cancelled or might still finish.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation): The task cancellation article explains `CancellationTokenSource`, token checks and how cancelled tasks report `OperationCanceledException`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
