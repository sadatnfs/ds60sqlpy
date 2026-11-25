# csharp-047: Resilience, idempotency and unknown outcomes

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-046`

## Learning objectives

Make retried operations idempotent by storing receipts and rejecting conflicting reuse of an identifier. The central exercise is task 3: Implement a result lookup that does not execute the command again.

## Purpose and mental model

A failed observation is not always a failed operation. A server may commit a write before the client loses its response. Retrying that write can duplicate an effect unless the protocol includes an idempotency key or another reconciliation mechanism. Exactly-once effects require careful scope and durable coordination; a retry loop alone cannot create that guarantee.

Bound retry attempts and use a failure policy that distinguishes transient, permanent and unknown outcomes. Backoff helps avoid overload but does not fix an invalid request. This offline state machine demonstrates once-per-key application under a single-threaded in-memory contract. Production durability and concurrency require additional storage and transaction evidence.

## Vocabulary and concepts

**Idempotency key:** An identity used to recognize repeated requests.

**Transient failure:** A failure that may resolve without changing the request.

**Reconciliation:** Determining the actual state after an uncertain observation.

## How to run this lesson

`Ledger` is declared after `Main` and keeps results in an in-memory dictionary, so it forgets everything when the process exits and is not safe for concurrent callers. Treat it as a model of the decision rule: a known identity replays its stored receipt, and a new identity applies once.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

A dictionary of operation identities records prior results. Check identity before applying a side effect, and store the result with the effect under a single atomic boundary in a real durable implementation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var ledger = new Ledger();
      Check(ledger.Apply("op-1", 3) == 3, "first effect");
      Check(ledger.Apply("op-1", 3) == 3 && ledger.Total == 3,
            "replayed receipt");
    }
    Console.WriteLine("csharp-047: passed");
    await Task.CompletedTask;
  }

  public sealed class Ledger {
    private readonly Dictionary<string, (int Amount, int Result)> results =
        new();
    public int Total { get; private set; }
    public int Apply(string id, int amount) {
      if (results.TryGetValue(id, out var prior)) {
        if (prior.Amount != amount)
          throw new InvalidOperationException("payload conflict");
        return prior.Result;
      }
      Total = checked(Total + amount);
      results.Add(id, (amount, Total));
      return Total;
    }
  }
}
```

**Observe:** The repeated identity returns its prior result without increasing the total.

**Trace.** The first `Apply("op-1", 3)` finds no prior entry, so `Total` becomes 3 and the dictionary stores amount 3 with result 3. The second call with the same key finds that entry, sees an identical amount and returns the stored result 3 without touching `Total`. The check confirms both the replayed receipt and the unchanged total.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var ledger = new Ledger();
      ledger.Apply("op-1", 3);
      ledger.Apply("op-2", 3);
      Check(ledger.Total == 6, "distinct commands");
      bool rejected = false;
      try {
        ledger.Apply("op-1", 4);
      } catch (InvalidOperationException) {
        rejected = true;
      }
      Check(rejected, "same key cannot change payload");
    }
    Console.WriteLine("csharp-047: passed");
    await Task.CompletedTask;
  }

  public sealed class Ledger {
    private readonly Dictionary<string, (int Amount, int Result)> results =
        new();
    public int Total { get; private set; }
    public int Apply(string id, int amount) {
      if (results.TryGetValue(id, out var prior)) {
        if (prior.Amount != amount)
          throw new InvalidOperationException("payload conflict");
        return prior.Result;
      }
      Total = checked(Total + amount);
      results.Add(id, (amount, Total));
      return Total;
    }
  }
}
```

**Observe:** A new identity applies separately, while a changed payload under an old key is rejected.

**Trace.** op-1 and op-2 each apply once, so `Total` is 6. The retry `Apply("op-1", 4)` finds op-1 recorded with amount 3, sees a different amount and throws `InvalidOperationException` with the message payload conflict. Replaying op-1 with 3 at that point would return 3, its original receipt, not the current total of 6.

## Exercises

1. **Predict and explain.** Trace the effect and receipt for the repeated operation.

2. **Guided modification.** Add a third unique operation and predict the total.

3. **Independent construction.** Implement a result lookup that does not execute the command again.

4. **Diagnose a defect.** Diagnose retrying a write after an observer timeout with a fresh identity.

5. **Boundary evidence.** Test repeated identity with identical and conflicting payloads.

6. **Transfer and justify.** Design durable atomic storage for an effect and its receipt and state remaining failure modes.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.

For task 4, a retry that invents a fresh identity after a timeout looks new to the ledger, so a write that actually succeeded is applied twice; reuse the original identity for every retry. For task 2, adding op-3 with 5 after op-1 and op-2 brings the total to 11. For task 5, an identical replay returns the receipt and a conflicting one throws.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Replay a recorded result without applying again) before changing anything, and confirm its observation: The repeated identity returns its prior result without increasing the total.
2. Compare Example B (Distinguish a new operation) with Example A and name the first line whose behavior differs. Its observation is: A new identity applies separately, while a changed payload under an old key is rejected.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: This in-memory ledger does not survive restart and is not concurrent.

## Self-check and next step

Explain why the replay returns the stored result rather than the current total. Describe what goes wrong if the effect and the receipt are saved in two separate steps and the process stops between them. For task 6, name the store that commits both atomically and the failure modes it still leaves.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide's dictionary and exception topics cover `TryGetValue` lookups and the conflict signal the ledger raises.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
