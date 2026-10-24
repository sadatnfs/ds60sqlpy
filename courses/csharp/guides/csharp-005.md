# csharp-005: Boolean decisions and exhaustive alternatives

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-004`

## Learning objectives

Write a classifier for negative, zero and positive temperatures. Then choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.

## Purpose and mental model

A branch chooses one path based on a Boolean expression. Good branches expose the domain distinction, not just a compact operator chain. Short-circuit operators evaluate their right side only when needed, which lets a guard protect a later operation. This is a control-flow property, not merely a performance optimization.

For mutually exclusive categories, put the cases in an order that matches the domain and include a policy for values outside the range. A boundary such as zero should have a deliberate meaning. Testing values just below, exactly at and just above a threshold detects mistakes that a typical middle value will miss.

## Vocabulary and concepts

**Predicate:** An expression producing true or false.

**Short circuit:** Skipping an unnecessary right-hand expression.

**Boundary:** An input where a classification changes.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`&&` requires both conditions and stops after false; `||` stops after true. A switch expression returns one value from its matching arm. The discard pattern `_` can provide an explicit fallback but must not conceal invalid input.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: A guard prevents unsafe access

The left operand establishes the precondition needed by the right operand.

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
            string? label = null;
            Check(!(label != null && label.Length > 0), "guarded access");
            label = "ok";
            Check(label != null && label.Length == 2, "present label");
        }
        Console.WriteLine("csharp-005: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The missing value is handled without dereferencing null.

### Example B: Classify a threshold

Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category.

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
            string Classify(int score) => score switch { < 0 => "invalid", < 60 => "retry", <= 100 => "pass", _ => "invalid" };
            Check(Classify(59) == "retry", "below boundary");
            Check(Classify(60) == "pass", "at boundary");
            Check(Classify(101) == "invalid", "outside domain");
        }
        Console.WriteLine("csharp-005: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** 59 retries, 60 passes, and 101 is rejected.

## Exercises

1. **Predict and explain.** Trace which operands execute when label is null.

2. **Guided modification.** Change the classifier pass threshold to 70 and update boundary checks.

3. **Independent construction.** Write a classifier for negative, zero and positive temperatures.

4. **Diagnose a defect.** Find why replacing && with & can break a null guard.

5. **Boundary evidence.** Test the two ends of the valid score range and one value beyond each end.

6. **Transfer and justify.** Choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Predicate, Short circuit, Boundary without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-005: Boolean decisions and exhaustive alternatives.
Read courses/csharp/guides/csharp-005.md and courses/csharp/lessons/csharp-005.cs. Prerequisites: csharp-004.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-005_solution.cs and
courses/csharp/solutions/csharp-005_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
