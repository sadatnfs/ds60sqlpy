# csharp-013: Classes, constructors and encapsulated invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-012`

## Learning objectives

Encapsulate state in a class whose constructor and methods keep its invariants on every path. The central exercise is task 3: Implement a bounded inventory whose reservations never make stock negative.

## Purpose and mental model

A class can protect a state transition by admitting changes only through reviewed operations. A constructor establishes the initial invariant; methods preserve it. Private setters are useful only when the public operations actually enforce the domain rule. A property named Balance that any caller can replace with a negative number has no meaningful protection.

Model expected rejection distinctly from programming defects. A withdrawal larger than the available balance can be a normal false result. A negative withdrawal is malformed input and may merit an argument exception. State should remain unchanged on rejected operations. This failure atomicity is often more important than a compact implementation.

## Vocabulary and concepts

**Invariant:** A rule true for every externally visible valid state.

**Encapsulation:** Hiding representation behind controlled operations.

**Failure atomicity:** A failed operation leaves the prior valid state intact.

## How to run this lesson

`Wallet` is declared after `Main` as a sealed helper class, and both examples construct their own instance, so neither one sees the other's balance. Example B's negative spend throws `ArgumentOutOfRangeException`, which the example catches; a passing run has therefore exercised the rejection path.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

A constructor has the class name and no return type. `private set` permits mutation inside the class. `sealed` prevents inheritance when extension is not part of the design. Guard clauses reject invalid inputs before state changes.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var wallet = new Wallet(10);
      Check(wallet.TrySpend(4) && wallet.Balance == 6, "valid spend");
      Check(!wallet.TrySpend(7) && wallet.Balance == 6,
            "rejection retains balance");
    }
    Console.WriteLine("csharp-013: passed");
    await Task.CompletedTask;
  }

  public sealed class Wallet {
    public int Balance { get; private set; }
    public Wallet(int initial) {
      if (initial < 0)
        throw new ArgumentOutOfRangeException(nameof(initial));
      Balance = initial;
    }
    public bool TrySpend(int amount) {
      if (amount < 0)
        throw new ArgumentOutOfRangeException(nameof(amount));
      if (amount > Balance)
        return false;
      Balance -= amount;
      return true;
    }
  }
}
```

**Observe:** Spending 4 succeeds; spending 7 afterward fails without changing 6.

**Trace.** The constructor checks that 10 is not negative and stores it in `Balance`. `TrySpend(4)` passes the negative-amount guard, sees that 4 does not exceed 10, subtracts and returns true, leaving 6. `TrySpend(7)` finds that 7 exceeds 6 and returns false before the subtraction line, so Balance still reads 6. The order of the checks protects the state.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var wallet = new Wallet(5);
      bool rejected = false;
      try {
        wallet.TrySpend(-1);
      } catch (ArgumentOutOfRangeException) {
        rejected = true;
      }
      Check(rejected && wallet.Balance == 5, "malformed input keeps state");
      Check(wallet.TrySpend(0) && wallet.Balance == 5, "zero is allowed");
    }
    Console.WriteLine("csharp-013: passed");
    await Task.CompletedTask;
  }

  public sealed class Wallet {
    public int Balance { get; private set; }
    public Wallet(int initial) {
      if (initial < 0)
        throw new ArgumentOutOfRangeException(nameof(initial));
      Balance = initial;
    }
    public bool TrySpend(int amount) {
      if (amount < 0)
        throw new ArgumentOutOfRangeException(nameof(amount));
      if (amount > Balance)
        return false;
      Balance -= amount;
      return true;
    }
  }
}
```

**Observe:** Negative spending is rejected and zero is an accepted no-op.

**Trace.** The wallet starts with 5. `TrySpend(-1)` hits the first guard and throws before any comparison or subtraction, so the catch sets `rejected` while Balance remains 5. `TrySpend(0)` passes the guard, 0 does not exceed 5, and subtracting zero leaves 5, so the call returns true. A malformed request throws; a legal request that changes nothing succeeds.

## Exercises

1. **Predict and explain.** Trace the wallet state through successful and rejected spending.

2. **Guided modification.** Add a validated deposit operation.

3. **Independent construction.** Implement a bounded inventory whose reservations never make stock negative.

4. **Diagnose a defect.** Diagnose subtracting before checking affordability.

5. **Boundary evidence.** Test exactly the available amount, zero and a negative request.

6. **Transfer and justify.** Explain whether a shared wallet needs synchronization when several tasks may spend concurrently.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.

For task 4, move `Balance -= amount` above the affordability test: `TrySpend(7)` on a balance of 6 then returns false but leaves -1 behind, which is exactly the corruption the guard order prevents. For task 5, spending exactly the balance must succeed and leave 0, because the test is `amount > Balance`, not `>=`.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve a nonnegative balance) before changing anything, and confirm its observation: Spending 4 succeeds; spending 7 afterward fails without changing 6.
2. Compare Example B (Reject malformed operations) with Example A and name the first line whose behavior differs. Its observation is: Negative spending is rejected and zero is an accepted no-op.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Private fields alone do not establish a correct contract.

## Self-check and next step

Explain why `private set` alone does not guarantee a nonnegative balance. For a wallet holding 3, predict the return value and the final balance for spends of 3, 4, 0 and -2. For task 6, describe what can go wrong when two tasks pass the affordability check before either one subtracts.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# programming guide's pages on classes, constructors and access modifiers explain how a type controls who may change its state.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
