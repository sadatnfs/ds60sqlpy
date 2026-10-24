# csharp-003: Numeric range, checked overflow and decimal amounts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-002`

## Learning objectives

Calculate a decimal subtotal and tax, rounding only the final payable amount. Then design a quantity and currency contract that states overflow, rounding and invalid-input behavior.

## Purpose and mental model

Arithmetic has representation limits. An `int` has a finite range, so mathematically valid addition may overflow. C# supports checked contexts that reject integral overflow and unchecked contexts that wrap. Neither behavior should be chosen accidentally for business quantities. Floating-point arithmetic instead approximates most decimal fractions, so equality of independently calculated doubles often needs a scale-aware tolerance.

Use `decimal` when a decimal representation matches the domain, such as many monetary calculations. Decimal arithmetic still has finite precision and range. Specify rounding at a business boundary, including its midpoint rule, rather than rounding every intermediate operation. Keep currency and units explicit: a bare number does not identify what it measures.

## Vocabulary and concepts

**Overflow:** A result outside the representation range.

**Decimal:** A base-ten-oriented finite precision numeric type.

**Rounding policy:** A rule selecting a representable result at a stated precision.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`checked(expression)` asks for integral overflow detection in that expression. The `m` suffix selects decimal, while `0.1` defaults to double. `Math.Round(amount, 2, MidpointRounding.ToEven)` records both precision and tie policy.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Reject overflowing counts

The normal and failure paths separate an exceptional boundary from ordinary arithmetic.

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
            bool overflowed = false;
            try { int large = int.MaxValue; _ = checked(large + 1); }
            catch (OverflowException) { overflowed = true; }
            Check(overflowed, "overflow must be visible");
            Check(checked(100 + 20) == 120, "normal addition");
        }
        Console.WriteLine("csharp-003: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The maximum int plus one is rejected; 100 plus 20 is accepted.

### Example B: Preserve decimal intent

A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation.

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
            decimal amount = 0.1m + 0.2m;
            Check(amount == 0.3m, "decimal tenths");
            Check(Math.Round(2.345m, 2, MidpointRounding.ToEven) == 2.34m, "even midpoint");
            Check(Math.Round(2.345m, 2, MidpointRounding.AwayFromZero) == 2.35m, "away midpoint");
        }
        Console.WriteLine("csharp-003: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Two valid midpoint policies produce 2.34 and 2.35.

## Exercises

1. **Predict and explain.** Predict which arithmetic operation throws and explain the representation boundary.

2. **Guided modification.** Replace maximum plus one with minimum minus one and check the failure.

3. **Independent construction.** Calculate a decimal subtotal and tax, rounding only the final payable amount.

4. **Diagnose a defect.** Diagnose a price parsed as double and later converted to decimal. Explain where approximation entered.

5. **Boundary evidence.** Compare midpoint values immediately below, at and above the rounding boundary.

6. **Transfer and justify.** Design a quantity and currency contract that states overflow, rounding and invalid-input behavior.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

`checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Overflow, Decimal, Rounding policy without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-003: Numeric range, checked overflow and decimal amounts.
Read courses/csharp/guides/csharp-003.md and courses/csharp/lessons/csharp-003.cs. Prerequisites: csharp-002.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-003_solution.cs and
courses/csharp/solutions/csharp-003_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
