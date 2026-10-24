# csharp-002: Types, variables and explicit conversions

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-001`

## Learning objectives

Write a TryParse-based validator accepting only nonnegative whole-number quantities. Then design an input boundary for a percentage and document its accepted textual and numeric ranges.

## Purpose and mental model

A type describes the values an expression may hold and the operations available on those values. `int` represents a bounded whole number; `double` represents a binary floating-point approximation; `bool` represents a logical decision. A variable is a named storage location. Reassigning a variable changes its stored value, not its declared type.

`var` asks the compiler to infer a static type from the initializer. It does not make the variable dynamically typed. Conversions deserve attention because they can widen a range, lose fractional information, or fail. Put conversion at a visible boundary rather than scattering casts through a formula. First choose the meaning and units of the result, then choose its type.

## Vocabulary and concepts

**Static type:** The compile-time classification of an expression.

**Conversion:** A change from one type representation to another.

**Try pattern:** A Boolean success result paired with an output value.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`int count = 7` declares and initializes. `var inferred = 7` also produces an int. `(double)count` converts before an operator uses the value. `int.TryParse(text, out int parsed)` returns success separately from the output value; a failed parse must not silently mean a real zero.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Division depends on operand types

Converting after integer division would preserve the already truncated result. Operand conversion must happen before division.

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
            int whole = 7 / 2;
            double fraction = (double)7 / 2;
            Check(whole == 3, "integer division");
            Check(fraction == 3.5, "floating division");
        }
        Console.WriteLine("csharp-002: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The integer result is 3 and the floating result is 3.5.

### Example B: Parse an external representation

The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value.

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
            bool accepted = int.TryParse("42", out int value);
            bool rejected = int.TryParse("forty-two", out _);
            Check(accepted && value == 42, "valid count");
            Check(!rejected, "invalid count is not zero");
        }
        Console.WriteLine("csharp-002: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** 42 parses successfully; words fail without an exception.

## Exercises

1. **Predict and explain.** Predict the type and value of 7/2, 7/2.0 and (double)(7/2).

2. **Guided modification.** Change the operands to 8 and 2 and explain why that input hides the truncation difference.

3. **Independent construction.** Write a TryParse-based validator accepting only nonnegative whole-number quantities.

4. **Diagnose a defect.** Diagnose a conversion performed after integer division. Produce a fractional counterexample.

5. **Boundary evidence.** Test empty text, zero, a negative number and a number outside the int range.

6. **Transfer and justify.** Design an input boundary for a percentage and document its accepted textual and numeric ranges.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Static type, Conversion, Try pattern without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-002: Types, variables and explicit conversions.
Read courses/csharp/guides/csharp-002.md and courses/csharp/lessons/csharp-002.cs. Prerequisites: csharp-001.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-002_solution.cs and
courses/csharp/solutions/csharp-002_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
