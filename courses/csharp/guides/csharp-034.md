# csharp-034: Atomic operations and concurrent collections

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-033`

## Learning objectives

Use Interlocked and concurrent collections with pure update functions for correct concurrent counts. The central exercise is task 3: Build a concurrent frequency counter using pure update functions.

## Purpose and mental model

Interlocked provides atomic operations on supported locations, such as increment and compare-exchange. These operations are useful for simple shared state, but several individually atomic operations do not automatically form one atomic transaction. Match the mechanism to the complete invariant.

Concurrent collections make their documented operations thread-safe. Delegates passed to GetOrAdd or AddOrUpdate may execute more than once and outside internal locks. They should therefore avoid irreversible side effects. A dictionary value being safely published does not make a mutable object stored inside it automatically thread-safe.

## Vocabulary and concepts

**Interlocked:** Atomic operations on supported shared locations.

**Thread-safe operation:** An operation with a documented concurrency contract.

**Factory purity:** Avoiding externally visible effects in value construction callbacks.

## How to run this lesson

Example A updates a local integer from four tasks with `Interlocked.Increment`, and Example B shares a `ConcurrentDictionary<string, int>` across twenty tasks. Neither example takes a lock. Reading a missing key through the dictionary's indexer still throws `KeyNotFoundException`, as it does for a plain dictionary, so use `TryGetValue` when absence is legal.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Interlocked.Increment(ref value)` atomically updates one location. ConcurrentDictionary manages concurrent lookup/update operations. A factory must tolerate repeated evaluation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Count atomically

Each increment is one supported atomic operation rather than a compound unsynchronized expression.

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
      int count = 0;
      await Task.WhenAll(Enumerable.Range(0, 4).Select(
          _ => Task.Run(() => {
            for (int i = 0; i < 100; i++)
              Interlocked.Increment(ref count);
          })));
      Check(count == 400, "atomic count");
    }
    Console.WriteLine("csharp-034: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The atomic count is exactly 400.

**Trace.** `count` starts at 0. Each task loops 100 times and calls `Interlocked.Increment(ref count)`, which reads, adds one and writes as a single indivisible step, so no other thread can slip in between. Four tasks complete 400 such steps. `Task.WhenAll` waits for all of them, and the check finds exactly 400.

### Example B: Update one key safely

The update delegate is a pure calculation, so repeated evaluation cannot duplicate an external effect.

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
      var counts = new ConcurrentDictionary<string, int>();
      await Task.WhenAll(Enumerable.Range(0, 20).Select(
          _ => Task.Run(() => counts.AddOrUpdate(
                            "a", 1, (_, previous) => previous + 1))));
      Check(counts["a"] == 20, "concurrent key updates");
    }
    Console.WriteLine("csharp-034: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Twenty admitted updates produce 20.

**Trace.** The dictionary starts empty. The first task to reach key a stores 1, the add value. Every later task applies the update delegate, which receives the previous count and returns one more. Under contention, the dictionary retries an update whose input changed, so the delegate can run more than twenty times, yet each admitted update counts once and the final value is 20.

## Exercises

1. **Predict and explain.** Compare count++ with Interlocked.Increment.

2. **Guided modification.** Add a second independently counted key.

3. **Independent construction.** Build a concurrent frequency counter using pure update functions.

4. **Diagnose a defect.** Diagnose sending a message inside an AddOrUpdate delegate.

5. **Boundary evidence.** Test absent and already-present keys.

6. **Transfer and justify.** Explain why atomically updating two separate balances does not preserve a transfer invariant.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.

For task 4, sending a message inside the `AddOrUpdate` delegate can send duplicates, because a retried delegate runs again; keep the delegate a pure calculation and send after the call returns. For task 5, an absent key takes the add value, and a present one takes the update. `GetOrAdd` factories can also run more than once, though only one result is stored.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Count atomically) before changing anything, and confirm its observation: The atomic count is exactly 400.
2. Compare Example B (Update one key safely) with Example A and name the first line whose behavior differs. Its observation is: Twenty admitted updates produce 20.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Concurrent containers protect their own structure, not arbitrary objects stored inside them.

## Self-check and next step

Explain why `count++` from four tasks can finish below 400 while `Interlocked.Increment` cannot. Describe why the `AddOrUpdate` delegate must be free of side effects. For task 6, show the window in which two separate atomic updates to balances A and B leave money missing from both, and name a tool that closes it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `Interlocked` class reference and the guide to thread-safe collections explain atomic operations and the behavior of `ConcurrentDictionary`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-034: Atomic operations and concurrent collections.
Read courses/csharp/guides/csharp-034.md and courses/csharp/lessons/csharp-034.cs. Prerequisites: csharp-033.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-034_solution.cs and
courses/csharp/solutions/csharp-034_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
