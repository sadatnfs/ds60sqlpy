# csharp-028: Testing contracts with meaningful counterexamples

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-027`

## Learning objectives

Write table-driven checks for your inventory quantity validator. Then separate unit and integration evidence for a JSON file importer.

## Purpose and mental model

A test is useful when a plausible wrong implementation would fail it. Repeating the implementation expression on both sides of an assertion provides weak independence. Start from a contract, choose a normal case, a boundary case and a known misconception, then derive expected outcomes separately.

The classroom uses framework-free throwing checks so the default route needs no package download. A separate prepared project can use a test framework and a test runner. Keep deterministic unit tests focused on pure behavior, and label integration tests that exercise files, databases or networks. A passing unit test does not prove a dependency is configured correctly.

## Vocabulary and concepts

**Test oracle:** The independent rule deciding whether behavior is correct.

**Regression case:** A case preserving evidence of a previous defect.

**Boundary test:** A test at a transition or limit of the contract.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A table of inputs and expected values separates cases from the loop executing them. An exception assertion should check the intended category. Avoid sleep-based timing tests; coordinate concurrent states with explicit signals.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use independently derived cases

The literal expectations come from the stated clamp rule, not a duplicated implementation.

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
            var cases = new[] { (Input: -2, Expected: 0), (Input: 0, Expected: 0), (Input: 3, Expected: 3) };
            foreach (var test in cases) Check(ClampNonnegative(test.Input) == test.Expected, "clamp contract");
        }
        Console.WriteLine("csharp-028: passed");
        await Task.CompletedTask;
    }

    public static int ClampNonnegative(int value) => value < 0 ? 0 : value;
}
```

**Observe:** Negative, zero and positive cases preserve their intended categories.

### Example B: Detect a plausible wrong function

A property complements examples but does not replace the domain-specific expected values.

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
            int Wrong(int value) => value <= 0 ? 1 : value;
            Check(Wrong(0) != ClampNonnegative(0), "boundary catches wrong default");
            Check(ClampNonnegative(ClampNonnegative(-4)) == ClampNonnegative(-4), "idempotence");
        }
        Console.WriteLine("csharp-028: passed");
        await Task.CompletedTask;
    }

    public static int ClampNonnegative(int value) => value < 0 ? 0 : value;
}
```

**Observe:** The zero case catches the incorrect default, and clamping twice changes nothing further.

## Exercises

1. **Predict and explain.** Explain which wrong implementations each case would reject.

2. **Guided modification.** Add an extreme integer case without overflow.

3. **Independent construction.** Write table-driven checks for your inventory quantity validator.

4. **Diagnose a defect.** Diagnose an assertion comparing a function call with the same call.

5. **Boundary evidence.** Test idempotence and an independently derived boundary value.

6. **Transfer and justify.** Separate unit and integration evidence for a JSON file importer.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Tests that always print success or catch their own assertion failures provide misleading evidence. A flaky test weakens trust even when production code is correct. Random generation requires a reproducible seed and a clear oracle.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Test oracle, Regression case, Boundary test without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-028: Testing contracts with meaningful counterexamples.
Read courses/csharp/guides/csharp-028.md and courses/csharp/lessons/csharp-028.cs. Prerequisites: csharp-027.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-028_solution.cs and
courses/csharp/solutions/csharp-028_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
