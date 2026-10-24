# csharp-017: Interfaces and substitutable behavior

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-016`

## Learning objectives

Define a small interface for a deterministic label formatter. Then choose one dependency worth injecting in the inventory importer and explain the testing benefit.

## Purpose and mental model

An interface states what a consumer may ask a component to do. It does not promise that every implementation has the same internal representation. A useful interface captures a stable responsibility: calculating a price, reading a record or producing a time value. Interfaces invented for every class can add indirection without improving the design.

Substitution is behavioral. Two implementations with the same method signature can still disagree about nulls, errors or units. Write those contracts and test the consumer with more than one implementation. This is also the beginning of dependency injection: a caller supplies the collaborator instead of letting the consumer construct an invisible global dependency.

## Vocabulary and concepts

**Interface:** A named behavioral contract.

**Substitution:** Using an implementation without breaking consumer expectations.

**Dependency injection:** Supplying a collaborator from outside the consumer.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`interface IRate` declares a method contract. A class implements that interface and supplies the method body. A variable typed as the interface exposes the contract, while dynamic dispatch chooses the implementation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use a declared contract

The consumer depends on the interface rather than the concrete class.

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
            IRate rate = new FlatRate(3);
            Check(rate.Cost(4) == 12, "flat rate");
            Check(Total(rate, 0) == 0, "consumer uses contract");
        }
        Console.WriteLine("csharp-017: passed");
        await Task.CompletedTask;
    }

    public interface IRate { int Cost(int units); }
    public sealed record FlatRate(int Price) : IRate { public int Cost(int units) => checked(Price * units); }
    public sealed record CappedRate(int Price, int Cap) : IRate { public int Cost(int units) => Math.Min(checked(Price * units), Cap); }
    public static int Total(IRate rate, int units) => rate.Cost(units);
}
```

**Observe:** Four units cost 12 and zero units cost zero.

### Example B: Change policy without changing the consumer

An implementation can change the pricing rule while preserving units and accepted inputs.

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
            IRate rate = new CappedRate(3, 10);
            Check(Total(rate, 4) == 10, "capped policy");
            Check(Total(new FlatRate(3), 4) == 12, "same consumer, different policy");
        }
        Console.WriteLine("csharp-017: passed");
        await Task.CompletedTask;
    }

    public interface IRate { int Cost(int units); }
    public sealed record FlatRate(int Price) : IRate { public int Cost(int units) => checked(Price * units); }
    public sealed record CappedRate(int Price, int Cap) : IRate { public int Cost(int units) => Math.Min(checked(Price * units), Cap); }
    public static int Total(IRate rate, int units) => rate.Cost(units);
}
```

**Observe:** The same consumer applies a capped or uncapped policy.

## Exercises

1. **Predict and explain.** Trace the interface call to the selected implementation.

2. **Guided modification.** Add a second flat rate and keep Total unchanged.

3. **Independent construction.** Define a small interface for a deterministic label formatter.

4. **Diagnose a defect.** Diagnose an implementation returning cents where the contract requires whole currency units.

5. **Boundary evidence.** Test zero and a value exactly at the cap.

6. **Transfer and justify.** Choose one dependency worth injecting in the inventory importer and explain the testing benefit.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Interface, Substitution, Dependency injection without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-017: Interfaces and substitutable behavior.
Read courses/csharp/guides/csharp-017.md and courses/csharp/lessons/csharp-017.cs. Prerequisites: csharp-016.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-017_solution.cs and
courses/csharp/solutions/csharp-017_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
