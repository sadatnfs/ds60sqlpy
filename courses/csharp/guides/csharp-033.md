# csharp-033: Threads, locks and compound invariants

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-032`

## Learning objectives

Implement a locked transfer preserving the sum of two balances. Then choose immutable snapshots or a lock for a shared report cache and justify the ownership model.

## Purpose and mental model

Concurrency permits operations to overlap. A data race occurs when unsynchronized access to shared mutable state violates the required memory and ordering rules. Even an apparently simple increment includes read, calculation and write, so it is not automatically atomic. Correctness requires protecting the entire invariant, not just individual fields.

A lock establishes mutual exclusion and ordering for code using the same lock object. Keep the protected region small and avoid awaiting while holding a synchronous lock. Never choose a publicly accessible object or a mutable value as the lock identity. Deadlock is a separate risk when multiple locks are acquired in conflicting orders; a single documented ordering can prevent that class of cycle.

## Vocabulary and concepts

**Atomicity:** An operation behaving as one indivisible state transition.

**Mutual exclusion:** Only one participant enters a protected region at a time.

**Deadlock:** A cycle of waiting that prevents progress.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`lock (gate)` enters a protected region and exits even on exceptions. All accesses participating in the invariant must use the same gate. Task.WhenAll observes the completion of the scheduled work.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Protect increments

The lock protects the read-modify-write transition, so the expected count does not depend on scheduling.

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
      var counter = new LockedCounter();
      await Task.WhenAll(Enumerable.Range(0, 4).Select(
          _ => Task.Run(() => {
            for (int i = 0; i < 100; i++)
              counter.Add();
          })));
      Check(counter.Value == 400, "all protected increments");
    }
    Console.WriteLine("csharp-033: passed");
    await Task.CompletedTask;
  }

  public sealed class LockedCounter {
    private readonly object gate = new();
    private int value;
    public void Add() { lock (gate) value++; }
    public int Value {
      get { lock (gate) return value; }
    }
  }
}
```

**Observe:** Four tasks produce exactly 400 increments.

### Example B: Protect a multi-field invariant

A synchronized writer with an unsynchronized reader does not establish the same contract.

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
      var account = new LockedCounter();
      account.Add();
      account.Add();
      Check(account.Value == 2, "consistent observation");
      Check(account.Value >= 0, "valid state");
    }
    Console.WriteLine("csharp-033: passed");
    await Task.CompletedTask;
  }

  public sealed class LockedCounter {
    private readonly object gate = new();
    private int value;
    public void Add() { lock (gate) value++; }
    public int Value {
      get { lock (gate) return value; }
    }
  }
}
```

**Observe:** The reader uses the same gate as mutation.

## Exercises

1. **Predict and explain.** Decompose an increment into its logical steps.

2. **Guided modification.** Increase task count while keeping the exact expected total.

3. **Independent construction.** Implement a locked transfer preserving the sum of two balances.

4. **Diagnose a defect.** Describe a two-lock acquisition cycle and repair it with an ordering rule.

5. **Boundary evidence.** Test zero operations and concurrent readers.

6. **Transfer and justify.** Choose immutable snapshots or a lock for a shared report cache and justify the ownership model.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Atomicity, Mutual exclusion, Deadlock without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-033: Threads, locks and compound invariants.
Read courses/csharp/guides/csharp-033.md and courses/csharp/lessons/csharp-033.cs. Prerequisites: csharp-032.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-033_solution.cs and
courses/csharp/solutions/csharp-033_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
