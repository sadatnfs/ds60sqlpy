# csharp-034: Atomic operations and concurrent collections

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-033`

## Learning objectives

Build a concurrent frequency counter using pure update functions. Then explain why atomically updating two separate balances does not preserve a transfer invariant.

## Purpose and mental model

Interlocked provides atomic operations on supported locations, such as increment and compare-exchange. These operations are useful for simple shared state, but several individually atomic operations do not automatically form one atomic transaction. Match the mechanism to the complete invariant.

Concurrent collections make their documented operations thread-safe. Delegates passed to GetOrAdd or AddOrUpdate may execute more than once and outside internal locks. They should therefore avoid irreversible side effects. A dictionary value being safely published does not make a mutable object stored inside it automatically thread-safe.

## Vocabulary and concepts

**Interlocked:** Atomic operations on supported shared locations.

**Thread-safe operation:** An operation with a documented concurrency contract.

**Factory purity:** Avoiding externally visible effects in value construction callbacks.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Interlocked.Increment(ref value)` atomically updates one location. ConcurrentDictionary manages concurrent lookup/update operations. A factory must tolerate repeated evaluation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            int count = 0;
            await Task.WhenAll(Enumerable.Range(0, 4).Select(_ => Task.Run(() => { for (int i = 0; i < 100; i++) Interlocked.Increment(ref count); })));
            Check(count == 400, "atomic count");
        }
        Console.WriteLine("csharp-034: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The atomic count is exactly 400.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            var counts = new ConcurrentDictionary<string, int>();
            await Task.WhenAll(Enumerable.Range(0, 20).Select(_ => Task.Run(() => counts.AddOrUpdate("a", 1, (_, previous) => previous + 1))));
            Check(counts["a"] == 20, "concurrent key updates");
        }
        Console.WriteLine("csharp-034: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Twenty admitted updates produce 20.

## Exercises

1. **Predict and explain.** Compare count++ with Interlocked.Increment.

2. **Guided modification.** Add a second independently counted key.

3. **Independent construction.** Build a concurrent frequency counter using pure update functions.

4. **Diagnose a defect.** Diagnose sending a message inside an AddOrUpdate delegate.

5. **Boundary evidence.** Test absent and already-present keys.

6. **Transfer and justify.** Explain why atomically updating two separate balances does not preserve a transfer invariant.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Interlocked, Thread-safe operation, Factory purity without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
