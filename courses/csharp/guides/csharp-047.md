# csharp-047: Resilience, idempotency and unknown outcomes

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-046`

## Learning objectives

Implement a result lookup that does not execute the command again. Then design durable atomic storage for an effect and its receipt and state remaining failure modes.

## Purpose and mental model

A failed observation is not always a failed operation. A server may commit a write before the client loses its response. Retrying that write can duplicate an effect unless the protocol includes an idempotency key or another reconciliation mechanism. Exactly-once effects require careful scope and durable coordination; a retry loop alone cannot create that guarantee.

Bound retry attempts and use a failure policy that distinguishes transient, permanent and unknown outcomes. Backoff helps avoid overload but does not fix an invalid request. This offline state machine demonstrates once-per-key application under a single-threaded in-memory contract. Production durability and concurrency require additional storage and transaction evidence.

## Vocabulary and concepts

**Idempotency key:** An identity used to recognize repeated requests.

**Transient failure:** A failure that may resolve without changing the request.

**Reconciliation:** Determining the actual state after an uncertain observation.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A dictionary of operation identities records prior results. Check identity before applying a side effect, and store the result with the effect under a single atomic boundary in a real durable implementation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Replay a recorded result without applying again

Operation identity separates a replay from a genuinely new command.

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
            var ledger = new Ledger();
            Check(ledger.Apply("op-1", 3) == 3, "first effect");
            Check(ledger.Apply("op-1", 3) == 3 && ledger.Total == 3, "replayed receipt");
        }
        Console.WriteLine("csharp-047: passed");
        await Task.CompletedTask;
    }

    public sealed class Ledger { private readonly Dictionary<string, (int Amount, int Result)> results = new(); public int Total { get; private set; } public int Apply(string id, int amount) { if (results.TryGetValue(id, out var prior)) { if (prior.Amount != amount) throw new InvalidOperationException("payload conflict"); return prior.Result; } Total = checked(Total + amount); results.Add(id, (amount, Total)); return Total; } }
}
```

**Observe:** The repeated identity returns its prior result without increasing the total.

### Example B: Distinguish a new operation

Idempotency keys need a payload consistency rule or they can hide conflicting requests.

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
            var ledger = new Ledger();
            ledger.Apply("op-1", 3); ledger.Apply("op-2", 3);
            Check(ledger.Total == 6, "distinct commands");
            bool rejected = false;
            try { ledger.Apply("op-1", 4); } catch (InvalidOperationException) { rejected = true; }
            Check(rejected, "same key cannot change payload");
        }
        Console.WriteLine("csharp-047: passed");
        await Task.CompletedTask;
    }

    public sealed class Ledger { private readonly Dictionary<string, (int Amount, int Result)> results = new(); public int Total { get; private set; } public int Apply(string id, int amount) { if (results.TryGetValue(id, out var prior)) { if (prior.Amount != amount) throw new InvalidOperationException("payload conflict"); return prior.Result; } Total = checked(Total + amount); results.Add(id, (amount, Total)); return Total; } }
}
```

**Observe:** A new identity applies separately, while a changed payload under an old key is rejected.

## Exercises

1. **Predict and explain.** Trace the effect and receipt for the repeated operation.

2. **Guided modification.** Add a third unique operation and predict the total.

3. **Independent construction.** Implement a result lookup that does not execute the command again.

4. **Diagnose a defect.** Diagnose retrying a write after an observer timeout with a fresh identity.

5. **Boundary evidence.** Test repeated identity with identical and conflicting payloads.

6. **Transfer and justify.** Design durable atomic storage for an effect and its receipt and state remaining failure modes.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Idempotency key, Transient failure, Reconciliation without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-047: Resilience, idempotency and unknown outcomes.
Read courses/csharp/guides/csharp-047.md and courses/csharp/lessons/csharp-047.cs. Prerequisites: csharp-046.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-047_solution.cs and
courses/csharp/solutions/csharp-047_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
