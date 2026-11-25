# csharp-033: Threads, locks and compound invariants

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-032`

## Learning objectives

Protect compound invariants with a lock so concurrent updates never expose a half-finished change. The central exercise is task 3: Implement a locked transfer preserving the sum of two balances.

## Purpose and mental model

Concurrency permits operations to overlap. A data race occurs when unsynchronized access to shared mutable state violates the required memory and ordering rules. Even an apparently simple increment includes read, calculation and write, so it is not automatically atomic. Correctness requires protecting the entire invariant, not just individual fields.

A lock establishes mutual exclusion and ordering for code using the same lock object. Keep the protected region small and avoid awaiting while holding a synchronous lock. Never choose a publicly accessible object or a mutable value as the lock identity. Deadlock is a separate risk when multiple locks are acquired in conflicting orders; a single documented ordering can prevent that class of cycle.

## Vocabulary and concepts

**Atomicity:** An operation behaving as one indivisible state transition.

**Mutual exclusion:** Only one participant enters a protected region at a time.

**Deadlock:** A cycle of waiting that prevents progress.

## How to run this lesson

`LockedCounter` uses `System.Threading.Lock`, the dedicated lock type. Example A starts four tasks with `Task.Run`, so increments really do interleave across threads. If you store a `Lock` in an `object` variable and lock that, the compiler issues warning CS9216 about monitor-based locking.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`lock (gate)` enters a protected region and exits even on exceptions. All accesses participating in the invariant must use the same gate. Since .NET 9 and C# 13, `System.Threading.Lock` is the dedicated lock type: `lock` on a `Lock` uses its scope API, and the compiler warns when a `Lock` is converted to `object`. Task.WhenAll observes the completion of the scheduled work.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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
    private readonly Lock gate = new();
    private int value;
    public void Add() { lock (gate) value++; }
    public int Value {
      get { lock (gate) return value; }
    }
  }
}
```

**Observe:** Four tasks produce exactly 400 increments.

**Trace.** `count++` without protection is three steps: read the value, add one, write it back. Two threads can both read 10 and both write 11, losing an increment. Inside `lock (gate)`, only one thread at a time runs those steps, so every increment is applied once. Four tasks of 100 increments each produce exactly 400.

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
    private readonly Lock gate = new();
    private int value;
    public void Add() { lock (gate) value++; }
    public int Value {
      get { lock (gate) return value; }
    }
  }
}
```

**Observe:** The reader uses the same gate as mutation.

**Trace.** `Add` runs twice under the gate, so the stored value is 2. The `Value` getter also takes the gate before reading, so a reader never sees a value in the middle of an update. The checks confirm 2 and a nonnegative state. The same gate protects reads and writes, which makes them part of one contract.

## Exercises

1. **Predict and explain.** Decompose an increment into its logical steps.

2. **Guided modification.** Increase task count while keeping the exact expected total.

3. **Independent construction.** Implement a locked transfer preserving the sum of two balances.

4. **Diagnose a defect.** Describe a two-lock acquisition cycle and repair it with an ordering rule.

5. **Boundary evidence.** Test zero operations and concurrent readers.

6. **Transfer and justify.** Choose immutable snapshots or a lock for a shared report cache and justify the ownership model.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.

For task 4, the classic cycle is one thread holding the lock for account A while waiting for B, and another holding B while waiting for A; both wait forever. The repair is a global order, such as always locking the lower account id first. A stress run that passes without locks proves nothing, because races depend on timing.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Protect increments) before changing anything, and confirm its observation: Four tasks produce exactly 400 increments.
2. Compare Example B (Protect a multi-field invariant) with Example A and name the first line whose behavior differs. Its observation is: The reader uses the same gate as mutation.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A passing unsynchronized stress run does not prove absence of races.

## Self-check and next step

Write the three steps of an unsynchronized increment and show one interleaving that loses an update. Explain why the getter also takes the lock. For task 3, describe the lock order your transfer uses and how it keeps the sum of the two balances constant.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET threading articles cover the `lock` statement, the `System.Threading.Lock` type and best practices for managed threading.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
