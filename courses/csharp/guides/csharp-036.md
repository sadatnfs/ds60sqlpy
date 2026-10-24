# csharp-036: Garbage collection, pooling and retained memory

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-035`

## Learning objectives

Write a pooled-buffer helper with finally-based return. Then decide whether pooling is justified using allocation measurements and a stated lifetime contract.

## Purpose and mental model

The garbage collector reclaims unreachable managed objects. Reachability is not the same as usefulness: a global list or event subscription can keep an otherwise unwanted object alive. Resource cleanup still belongs to IDisposable rather than collection timing. Measure retained references before assuming the collector is malfunctioning.

ArrayPool reuses buffers to reduce allocation pressure. A rented array may be larger than requested and may contain prior data. Use only the logical length, initialize what will be read, and return exactly the borrowed array once. Clearing sensitive contents is a deliberate policy. Pooling adds ownership complexity, so it should solve a measured allocation problem.

## Vocabulary and concepts

**Reachability:** Whether a live reference path can still reach an object.

**Pool:** A reusable store of resources.

**Logical length:** The meaningful region distinct from physical capacity.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`ArrayPool<T>.Shared.Rent(n)` grants temporary use of at least n elements. `Return` ends ownership. A try/finally protects return on failure; never expose a view after return.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use only admitted buffer contents

The pool guarantees minimum capacity, not exact size or zeroed contents.

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
            int[] rented = ArrayPool<int>.Shared.Rent(3);
            try { rented[0] = 2; rented[1] = 3; rented[2] = 4; Check(rented.AsSpan(0, 3).ToArray().Sum() == 9, "logical range"); Check(rented.Length >= 3, "minimum capacity"); }
            finally { ArrayPool<int>.Shared.Return(rented, clearArray: true); }
        }
        Console.WriteLine("csharp-036: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Only three initialized elements contribute to the total.

### Example B: Release retained references deliberately

The test checks controllable ownership, avoiding a flaky assumption about when garbage collection occurs.

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
            var retained = new List<byte[]> { new byte[32], new byte[32] };
            Check(retained.Count == 2, "references retained");
            retained.Clear();
            Check(retained.Count == 0, "application releases references");
        }
        Console.WriteLine("csharp-036: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Clearing removes the application references without promising collection timing.

## Exercises

1. **Predict and explain.** Separate logical length from rented array length.

2. **Guided modification.** Use a different requested length while initializing exactly that region.

3. **Independent construction.** Write a pooled-buffer helper with finally-based return.

4. **Diagnose a defect.** Diagnose reading uninitialized pooled capacity or returning the same buffer twice.

5. **Boundary evidence.** Test cleanup when the computation throws.

6. **Transfer and justify.** Decide whether pooling is justified using allocation measurements and a stated lifetime contract.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Reachability, Pool, Logical length without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-036: Garbage collection, pooling and retained memory.
Read courses/csharp/guides/csharp-036.md and courses/csharp/lessons/csharp-036.cs. Prerequisites: csharp-035.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-036_solution.cs and
courses/csharp/solutions/csharp-036_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
