# csharp-013: Classes, constructors and encapsulated invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-012`

## Learning objectives

Implement a bounded inventory whose reservations never make stock negative. Then explain whether a shared wallet needs synchronization when several tasks may spend concurrently.

## Purpose and mental model

A class can protect a state transition by admitting changes only through reviewed operations. A constructor establishes the initial invariant; methods preserve it. Private setters are useful only when the public operations actually enforce the domain rule. A property named Balance that any caller can replace with a negative number has no meaningful protection.

Model expected rejection distinctly from programming defects. A withdrawal larger than the available balance can be a normal false result. A negative withdrawal is malformed input and may merit an argument exception. State should remain unchanged on rejected operations. This failure atomicity is often more important than a compact implementation.

## Vocabulary and concepts

**Invariant:** A rule true for every externally visible valid state.

**Encapsulation:** Hiding representation behind controlled operations.

**Failure atomicity:** A failed operation leaves the prior valid state intact.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A constructor has the class name and no return type. `private set` permits mutation inside the class. `sealed` prevents inheritance when extension is not part of the design. Guard clauses reject invalid inputs before state changes.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Preserve a nonnegative balance

Validate affordability before subtraction so rejected requests cannot corrupt state.

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
            var wallet = new Wallet(10);
            Check(wallet.TrySpend(4) && wallet.Balance == 6, "valid spend");
            Check(!wallet.TrySpend(7) && wallet.Balance == 6, "rejection retains balance");
        }
        Console.WriteLine("csharp-013: passed");
        await Task.CompletedTask;
    }

    public sealed class Wallet { public int Balance { get; private set; } public Wallet(int initial) { if (initial < 0) throw new ArgumentOutOfRangeException(nameof(initial)); Balance = initial; } public bool TrySpend(int amount) { if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount)); if (amount > Balance) return false; Balance -= amount; return true; } }
}
```

**Observe:** Spending 4 succeeds; spending 7 afterward fails without changing 6.

### Example B: Reject malformed operations

These are separate boundary policies. Both preserve the invariant, but they communicate different meanings to the caller.

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
            var wallet = new Wallet(5);
            bool rejected = false;
            try { wallet.TrySpend(-1); } catch (ArgumentOutOfRangeException) { rejected = true; }
            Check(rejected && wallet.Balance == 5, "malformed input keeps state");
            Check(wallet.TrySpend(0) && wallet.Balance == 5, "zero is allowed");
        }
        Console.WriteLine("csharp-013: passed");
        await Task.CompletedTask;
    }

    public sealed class Wallet { public int Balance { get; private set; } public Wallet(int initial) { if (initial < 0) throw new ArgumentOutOfRangeException(nameof(initial)); Balance = initial; } public bool TrySpend(int amount) { if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount)); if (amount > Balance) return false; Balance -= amount; return true; } }
}
```

**Observe:** Negative spending is rejected and zero is an accepted no-op.

## Exercises

1. **Predict and explain.** Trace the wallet state through successful and rejected spending.

2. **Guided modification.** Add a validated deposit operation.

3. **Independent construction.** Implement a bounded inventory whose reservations never make stock negative.

4. **Diagnose a defect.** Diagnose subtracting before checking affordability.

5. **Boundary evidence.** Test exactly the available amount, zero and a negative request.

6. **Transfer and justify.** Explain whether a shared wallet needs synchronization when several tasks may spend concurrently.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Invariant, Encapsulation, Failure atomicity without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-013: Classes, constructors and encapsulated invariants.
Read courses/csharp/guides/csharp-013.md and courses/csharp/lessons/csharp-013.cs. Prerequisites: csharp-012.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-013_solution.cs and
courses/csharp/solutions/csharp-013_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
