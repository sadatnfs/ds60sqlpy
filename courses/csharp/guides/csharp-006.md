# csharp-006: Loops, invariants and termination

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-005`

## Learning objectives

Implement a first-match search returning a separate not-found representation. Then design a bounded retry loop and explain both its invariant and its stopping argument.

## Purpose and mental model

A loop repeats a state transition. To understand it, state what is true before the first iteration and what remains true after each iteration. This repeated truth is an invariant. A second argument explains termination: some bounded quantity moves toward a stopping condition. A correct-looking body can still fail because its boundary executes once too often or never stops.

`foreach` expresses traversal of an existing sequence and usually avoids manual index bookkeeping. Use an index when the position itself matters, but relate the valid index range to the collection length. Empty inputs are especially revealing because the initial state becomes the final result without any iteration.

## Vocabulary and concepts

**Invariant:** A property maintained across iterations.

**Accumulator:** State summarizing the values seen so far.

**Termination:** An argument that repetition eventually stops.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`for (initial; condition; update)` initializes once, checks before each body, and updates after each body. For an array of Length n, valid indices are zero through n minus one. `break` exits the loop; `continue` skips the remainder of one iteration.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Sum with a maintained invariant

Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially.

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
            int[] values = { 2, 4, 6 };
            int sum = 0;
            foreach (int value in values) sum += value;
            Check(sum == 12, "sum of all values");
            Check(Array.Empty<int>().Sum() == 0, "empty sum identity");
        }
        Console.WriteLine("csharp-006: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The sum is 12 and the empty sum is zero.

### Example B: Locate the first match

Stopping at the first match is part of the contract. Without break, the same loop could return the last match.

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
            int[] values = { 3, 8, 8 };
            int found = -1;
            for (int i = 0; i < values.Length; i++) { if (values[i] == 8) { found = i; break; } }
            Check(found == 1, "first matching position");
            Check(!Array.Exists(values, value => value == 9), "absent target");
        }
        Console.WriteLine("csharp-006: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The first 8 is at index 1; 9 is absent.

## Exercises

1. **Predict and explain.** Write the accumulator value before and after every iteration in Example A.

2. **Guided modification.** Skip negative values while preserving the sum invariant.

3. **Independent construction.** Implement a first-match search returning a separate not-found representation.

4. **Diagnose a defect.** Diagnose the condition i <= values.Length using a one-element array.

5. **Boundary evidence.** Check empty, singleton, no-match and repeated-match inputs.

6. **Transfer and justify.** Design a bounded retry loop and explain both its invariant and its stopping argument.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Invariant, Accumulator, Termination without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-006: Loops, invariants and termination.
Read courses/csharp/guides/csharp-006.md and courses/csharp/lessons/csharp-006.cs. Prerequisites: csharp-005.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-006_solution.cs and
courses/csharp/solutions/csharp-006_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
