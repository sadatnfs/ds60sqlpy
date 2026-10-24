# csharp-012: Value copies, references and mutation ownership

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-011`

## Learning objectives

Choose a representation for a coordinate and for a shared session, explaining the difference. Then design a data boundary that prevents callers from mutating an internal collection.

## Purpose and mental model

Value and reference semantics describe what assignment copies. A value-type assignment copies the value. A reference-type assignment copies a reference, so both variables may reach the same object. This is more useful than the misleading slogan that values always live on the stack and objects always live on the heap: storage placement depends on context, while assignment semantics remain the reasoning tool.

A class can deliberately encapsulate mutation behind operations that preserve invariants. A value object can make independent copies easier to reason about. Neither choice is automatically faster or safer. Ask whether identity matters, whether consumers should share changes, and how large or expensive copies may become.

## Vocabulary and concepts

**Value semantics:** Assignment copies the represented value.

**Reference semantics:** Assignment copies a reference to shared identity.

**Ownership:** The responsibility for permitted mutation and lifetime.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`struct` introduces a value type; `class` introduces a reference type. Assignment has the same spelling for both, so inspect the declared type. `ReferenceEquals` asks whether references identify the same object, not whether their properties happen to match.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Copy a value

The struct contains only integer fields, so its copied state is independently mutable.

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
            var first = new Point(2, 3);
            var second = first;
            second.X = 9;
            Check(first.X == 2 && second.X == 9, "struct copy");
        }
        Console.WriteLine("csharp-012: passed");
        await Task.CompletedTask;
    }

    public struct Point { public int X; public int Y; public Point(int x, int y) { X = x; Y = y; } }
    public sealed class Counter { public int Value { get; set; } }
}
```

**Observe:** Changing the copied point leaves the original X at 2.

### Example B: Share an object identity

Passing or assigning a reference by value does not clone the referenced object.

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
            var first = new Counter();
            var second = first;
            second.Value++;
            Check(first.Value == 1, "shared mutation");
            Check(ReferenceEquals(first, second), "same object");
        }
        Console.WriteLine("csharp-012: passed");
        await Task.CompletedTask;
    }

    public struct Point { public int X; public int Y; public Point(int x, int y) { X = x; Y = y; } }
    public sealed class Counter { public int Value { get; set; } }
}
```

**Observe:** Both references observe the same counter increment.

## Exercises

1. **Predict and explain.** Draw the values and references after each assignment.

2. **Guided modification.** Make a separate Counter instance and compare identity with equal property values.

3. **Independent construction.** Choose a representation for a coordinate and for a shared session, explaining the difference.

4. **Diagnose a defect.** Diagnose expecting assignment of a class variable to produce a deep copy.

5. **Boundary evidence.** Place a mutable list inside a struct and explain which part of the copied value remains shared.

6. **Transfer and justify.** Design a data boundary that prevents callers from mutating an internal collection.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Value semantics, Reference semantics, Ownership without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-012: Value copies, references and mutation ownership.
Read courses/csharp/guides/csharp-012.md and courses/csharp/lessons/csharp-012.cs. Prerequisites: csharp-011.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-012_solution.cs and
courses/csharp/solutions/csharp-012_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
