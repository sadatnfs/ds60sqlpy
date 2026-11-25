# csharp-031: Bounded channels and producer-consumer ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-030`

## Learning objectives

Connect producers and consumers through bounded channels with explicit completion. The central exercise is task 3: Build a bounded producer-consumer pipeline with explicit writer completion.

## Purpose and mental model

A channel connects producers and consumers through an asynchronous queue. Capacity is a resource policy: an unbounded queue can retain more work than memory or downstream systems can handle. A bounded channel makes overload visible through waiting, rejection or an explicit drop policy. Choose that policy from the value of the work, not from convenience.

Completion means no more writes will be admitted, while readers can still drain buffered items. A consumer should distinguish an empty-but-open channel from a completed channel. Cancellation and failure also need owners: somebody must complete the writer and account for admitted items. The single-process fixture teaches these states without depending on thread timing.

## Vocabulary and concepts

**Backpressure:** Limiting admitted work when capacity is exhausted.

**Admission:** Acceptance of a work item into owned processing.

**Drain:** Processing already admitted items after writes stop.

## How to run this lesson

`Channel.CreateBounded<int>` comes from `System.Threading.Channels`, which the worked examples import. The default full mode is Wait, so `TryWrite` reports false when the buffer is full rather than dropping anything. A bounded channel created with `BoundedChannelFullMode.DropOldest` instead accepts the write and discards the oldest item.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Channel.CreateBounded<T>` creates a capacity-limited channel. TryWrite reports immediate admission. ReadAsync removes an item; Writer.Complete closes admission. Reader.Completion finishes after buffered work is drained.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Reject immediate excess admission

Bounded capacity is observable before work is lost or memory grows without limit.

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
      var channel = Channel.CreateBounded<int>(1);
      Check(channel.Writer.TryWrite(4), "first item admitted");
      Check(!channel.Writer.TryWrite(5), "capacity reached");
      Check(await channel.Reader.ReadAsync() == 4, "admitted value retained");
    }
    Console.WriteLine("csharp-031: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The first item is accepted and the second immediate write is refused.

**Trace.** The channel holds at most one item. `TryWrite(4)` finds space, stores 4 and returns true. `TryWrite(5)` finds the buffer full and returns false immediately; 5 was never admitted. `ReadAsync` removes 4 and returns it, leaving the channel empty and open. The producer learned about the full buffer from the Boolean.

### Example B: Drain after completion

Closing admission does not discard buffered work. Completion becomes final after the reader drains it.

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
      var channel = Channel.CreateBounded<int>(2);
      channel.Writer.TryWrite(2);
      channel.Writer.TryWrite(3);
      channel.Writer.Complete();
      int sum = 0;
      await foreach (int value in channel.Reader.ReadAllAsync()) sum += value;
      await channel.Reader.Completion;
      Check(sum == 5 && !channel.Writer.TryWrite(9), "drained and closed");
    }
    Console.WriteLine("csharp-031: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Both admitted items are read after completion, and later writes fail.

**Trace.** With capacity two, both writes succeed and then `Complete()` closes admission while 2 and 3 stay buffered. `ReadAllAsync` yields 2 and 3 and ends because the channel is complete and empty. `Reader.Completion` then finishes. The sum is 5, and `TryWrite(9)` returns false because writing after completion is refused, even though the buffer now has room.

## Exercises

1. **Predict and explain.** Trace channel occupancy after each operation.

2. **Guided modification.** Increase capacity and predict which immediate writes succeed.

3. **Independent construction.** Build a bounded producer-consumer pipeline with explicit writer completion.

4. **Diagnose a defect.** Diagnose treating an empty open channel as permanently finished.

5. **Boundary evidence.** Test completion with zero buffered items and with a full buffer.

6. **Transfer and justify.** Choose wait, reject or drop behavior for a workload and explain what evidence the producer receives.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An ignored false TryWrite result loses work. Blocking a producer while holding a lock needed by the consumer can deadlock. Completion and cancellation need a deliberate ownership policy.

For task 4, an empty open channel is not finished: `TryRead` returns false while `Reader.Completion.IsCompleted` is still false. Only after `Complete()` and draining does `ReadAsync` throw `ChannelClosedException`. For task 5, completing with zero buffered items makes `ReadAllAsync` end immediately, and the loop body never runs.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Reject immediate excess admission) before changing anything, and confirm its observation: The first item is accepted and the second immediate write is refused.
2. Compare Example B (Drain after completion) with Example A and name the first line whose behavior differs. Its observation is: Both admitted items are read after completion, and later writes fail.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An ignored false TryWrite result loses work.

## Self-check and next step

List the channel's contents after each operation in Example A. Explain what the producer must do with a false `TryWrite` result. For task 6, choose Wait, reject or DropOldest for a stream of sensor readings and for a stream of payments, and say what each producer learns.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET channels article covers bounded and unbounded channels, full modes, completion and the reader and writer APIs.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-031: Bounded channels and producer-consumer ownership.
Read courses/csharp/guides/csharp-031.md and courses/csharp/lessons/csharp-031.cs. Prerequisites: csharp-030.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-031_solution.cs and
courses/csharp/solutions/csharp-031_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
