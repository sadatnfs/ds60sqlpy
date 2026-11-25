# csharp-029: Async, await and task completion

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-028`

## Learning objectives

Write async methods that await results, propagate failures and keep input order with Task.WhenAll. The central exercise is task 3: Write an async method returning a validated total.

## Purpose and mental model

A Task represents eventual completion, failure or cancellation. Async methods let control return to a caller while an awaited operation is incomplete. Async does not automatically mean a new thread, and awaiting a task does not block a thread in the same way as calling Wait or Result. For I/O, the goal is to avoid holding a thread idle while another system works.

Keep task ownership visible: the caller should await work whose result or failure matters. Fire-and-forget work can outlive its owner and lose exceptions. CPU-heavy work has different scheduling needs from asynchronous I/O. This chapter uses already completed and explicitly coordinated tasks so results do not depend on network access or arbitrary delays.

## Vocabulary and concepts

**Task:** A handle for eventual completion and its outcome.

**Await:** An asynchronous wait that observes the task result.

**Composition:** Combining smaller asynchronous operations into an owned result.

## How to run this lesson

`Main` is declared `async` in this lesson so that the examples can use `await` at the top level of each block. Every task in the examples is already complete when it is created, through `Task.FromResult` or `Task.FromException`, so the run is fast and deterministic and no real waiting happens.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`async Task<int>` declares an asynchronous result. `await` obtains the completed result or rethrows the task failure. Task.WhenAll combines completion of several tasks; its result order follows the input task order, not completion order.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Await values explicitly

The task handle and the eventual integer are distinct values even when this fixture completes immediately.

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
      Task<int> pending = Task.FromResult(7);
      int value = await pending;
      Check(value == 7 && pending.IsCompletedSuccessfully,
            "observed completion");
    }
    Console.WriteLine("csharp-029: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Await yields 7 and confirms successful completion.

**Trace.** `Task.FromResult(7)` returns a `Task<int>` that has already completed with 7. `pending` holds the task, not the integer. `await pending` finds the task complete, extracts 7 and assigns it to `value`. `IsCompletedSuccessfully` is true because the task ended with a result rather than an exception or cancellation. Awaiting a completed task continues without suspending.

### Example B: Compose and observe failure

Awaiting establishes ownership of both success and failure instead of losing an unobserved background result.

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
      int[] values = await Task.WhenAll(Task.FromResult(2), Task.FromResult(3));
      Check(values.SequenceEqual(new[] { 2, 3 }), "input order retained");
      bool observed = false;
      try {
        await Task.FromException<int>(new InvalidOperationException("fixture"));
      } catch (InvalidOperationException) {
        observed = true;
      }
      Check(observed, "failure propagated through await");
    }
    Console.WriteLine("csharp-029: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** WhenAll retains input order and await exposes the task exception.

**Trace.** `Task.WhenAll` receives two completed tasks and returns a task whose result is an array in input order, 2 then 3. The second part awaits a task created already faulted with `InvalidOperationException`; `await` rethrows that exception, and the catch sets `observed`. The failure surfaced only because something awaited the task and caught it.

## Exercises

1. **Predict and explain.** Distinguish the Task<int> handle from its awaited integer.

2. **Guided modification.** Combine three completed tasks and predict output ordering.

3. **Independent construction.** Write an async method returning a validated total.

4. **Diagnose a defect.** Diagnose forgetting to await an operation whose failure matters.

5. **Boundary evidence.** Test successful, failed and empty WhenAll inputs.

6. **Transfer and justify.** Explain when CPU work might need scheduling separately from an asynchronous I/O API.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Async void is mainly for required event-handler signatures, not general composable methods. Blocking with Result can deadlock in synchronization contexts. Task.Run does not make a blocking external API inherently scalable.

For task 5, `Task.WhenAll` over an empty array completes at once with an empty result. When two inputs both fail, `await` rethrows only the first exception, while the combined task's `Exception.InnerExceptions` holds both, here 2. For task 4, a task that is never awaited can fail without anyone seeing the exception.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Await values explicitly) before changing anything, and confirm its observation: Await yields 7 and confirms successful completion.
2. Compare Example B (Compose and observe failure) with Example A and name the first line whose behavior differs. Its observation is: WhenAll retains input order and await exposes the task exception.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Async void is mainly for required event-handler signatures, not general composable methods.

## Self-check and next step

Give the types of `pending` and `value` in Example A. Explain the order of results from `WhenAll` when the second task finishes first. For task 6, describe a CPU-heavy computation that belongs on `Task.Run` and an I/O call that should be awaited directly without it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The asynchronous programming articles in the C# guide explain `async`, `await`, `Task` composition and exception propagation.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-029: Async, await and task completion.
Read courses/csharp/guides/csharp-029.md and courses/csharp/lessons/csharp-029.cs. Prerequisites: csharp-028.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-029_solution.cs and
courses/csharp/solutions/csharp-029_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
