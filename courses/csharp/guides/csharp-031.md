# csharp-031: Bounded channels and producer-consumer ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-030`

## Learning objectives

Build a bounded producer-consumer pipeline with explicit writer completion. Then choose wait, reject or drop behavior for a workload and explain what evidence the producer receives.

## Purpose and mental model

A channel connects producers and consumers through an asynchronous queue. Capacity is a resource policy: an unbounded queue can retain more work than memory or downstream systems can handle. A bounded channel makes overload visible through waiting, rejection or an explicit drop policy. Choose that policy from the value of the work, not from convenience.

Completion means no more writes will be admitted, while readers can still drain buffered items. A consumer should distinguish an empty-but-open channel from a completed channel. Cancellation and failure also need owners: somebody must complete the writer and account for admitted items. The single-process fixture teaches these states without depending on thread timing.

## Vocabulary and concepts

**Backpressure:** Limiting admitted work when capacity is exhausted.

**Admission:** Acceptance of a work item into owned processing.

**Drain:** Processing already admitted items after writes stop.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Channel.CreateBounded<T>` creates a capacity-limited channel. TryWrite reports immediate admission. ReadAsync removes an item; Writer.Complete closes admission. Reader.Completion finishes after buffered work is drained.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Trace channel occupancy after each operation.

2. **Guided modification.** Increase capacity and predict which immediate writes succeed.

3. **Independent construction.** Build a bounded producer-consumer pipeline with explicit writer completion.

4. **Diagnose a defect.** Diagnose treating an empty open channel as permanently finished.

5. **Boundary evidence.** Test completion with zero buffered items and with a full buffer.

6. **Transfer and justify.** Choose wait, reject or drop behavior for a workload and explain what evidence the producer receives.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An ignored false TryWrite result loses work. Blocking a producer while holding a lock needed by the consumer can deadlock. Completion and cancellation need a deliberate ownership policy.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Backpressure, Admission, Drain without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
