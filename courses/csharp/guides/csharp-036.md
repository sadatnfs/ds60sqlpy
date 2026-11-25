# csharp-036: Garbage collection, pooling and retained memory

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-035`

## Learning objectives

Rent and return pooled buffers with finally and reason about retained memory. The central exercise is task 3: Write a pooled-buffer helper with finally-based return.

## Purpose and mental model

The garbage collector reclaims unreachable managed objects. Reachability is not the same as usefulness: a global list or event subscription can keep an otherwise unwanted object alive. Resource cleanup still belongs to IDisposable rather than collection timing. Measure retained references before assuming the collector is malfunctioning.

ArrayPool reuses buffers to reduce allocation pressure. A rented array may be larger than requested and may contain prior data. Use only the logical length, initialize what will be read, and return exactly the borrowed array once. Clearing sensitive contents is a deliberate policy. Pooling adds ownership complexity, so it should solve a measured allocation problem.

## Vocabulary and concepts

**Reachability:** Whether a live reference path can still reach an object.

**Pool:** A reusable store of resources.

**Logical length:** The meaningful region distinct from physical capacity.

## How to run this lesson

`ArrayPool<int>.Shared` comes from `System.Buffers`, which the worked examples import. In this runtime, `Rent(3)` returned an array of length 16 and `Rent(17)` returned 32, but only the minimum length is promised, so the example sums a span of exactly three elements rather than the whole array.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`ArrayPool<T>.Shared.Rent(n)` grants temporary use of at least n elements. `Return` ends ownership. A try/finally protects return on failure; never expose a view after return.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int[] rented = ArrayPool<int>.Shared.Rent(3);
      try {
        rented[0] = 2;
        rented[1] = 3;
        rented[2] = 4;
        Check(rented.AsSpan(0, 3).ToArray().Sum() == 9, "logical range");
        Check(rented.Length >= 3, "minimum capacity");
      } finally {
        ArrayPool<int>.Shared.Return(rented, clearArray: true);
      }
    }
    Console.WriteLine("csharp-036: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Only three initialized elements contribute to the total.

**Trace.** `Rent(3)` hands out an array with at least three elements, possibly reused and possibly holding old values. The code writes 2, 3 and 4 into the first three slots, views exactly that range and sums it to 9. The second check asserts only the minimum length. `finally` returns the array with `clearArray: true`, so the next renter sees zeros.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
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

**Trace.** `retained` holds two 32-byte arrays, so the application keeps both alive. `Clear()` removes the references and Count becomes 0. The check makes no claim about when the garbage collector reclaims the arrays: once nothing refers to them they become eligible, and the timing belongs to the runtime, not to this program.

## Exercises

1. **Predict and explain.** Separate logical length from rented array length.

2. **Guided modification.** Use a different requested length while initializing exactly that region.

3. **Independent construction.** Write a pooled-buffer helper with finally-based return.

4. **Diagnose a defect.** Diagnose reading uninitialized pooled capacity or returning the same buffer twice.

5. **Boundary evidence.** Test cleanup when the computation throws.

6. **Transfer and justify.** Decide whether pooling is justified using allocation measurements and a stated lifetime contract.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.

For task 4, summing the whole rented array instead of the initialized span reads whatever earlier renters left in slots 3 through 15. Returning the same array twice lets the pool hand it to two renters at once, which corrupts both silently. For task 5, the `finally` block must return the buffer even when the computation throws.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use only admitted buffer contents) before changing anything, and confirm its observation: Only three initialized elements contribute to the total.
2. Compare Example B (Release retained references deliberately) with Example A and name the first line whose behavior differs. Its observation is: Clearing removes the application references without promising collection timing.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Never assert that a weak reference must disappear immediately after a collection request.

## Self-check and next step

State the logical length and the rented length in Example A, and which one your code may rely on. Explain why the example avoids asserting that memory has been collected. For task 6, name the allocation measurement that would justify pooling and the lifetime rule each borrower must follow.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET garbage collection fundamentals and the `ArrayPool<T>` reference describe generations, reachability and buffer renting.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
