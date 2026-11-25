# csharp-017: Interfaces and substitutable behavior

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-016`

## Learning objectives

Program against an interface so different policies can be substituted without changing the consumer. The central exercise is task 3: Define a small interface for a deterministic label formatter.

## Purpose and mental model

An interface states what a consumer may ask a component to do. It does not promise that every implementation has the same internal representation. A useful interface captures a stable responsibility: calculating a price, reading a record or producing a time value. Interfaces invented for every class can add indirection without improving the design.

Substitution is behavioral. Two implementations with the same method signature can still disagree about nulls, errors or units. Write those contracts and test the consumer with more than one implementation. This is also the beginning of dependency injection: a caller supplies the collaborator instead of letting the consumer construct an invisible global dependency.

## Vocabulary and concepts

**Interface:** A named behavioral contract.

**Substitution:** Using an implementation without breaking consumer expectations.

**Dependency injection:** Supplying a collaborator from outside the consumer.

## How to run this lesson

`IRate`, `FlatRate`, `CappedRate` and `Total` are declared after `Main`. Both rate types are sealed positional records that implement the interface, so each example builds a rate with one expression. Multiplication is checked, so an extreme unit count throws `OverflowException` instead of returning a negative price.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`interface IRate` declares a method contract. A class implements that interface and supplies the method body. A variable typed as the interface exposes the contract, while dynamic dispatch chooses the implementation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      IRate rate = new FlatRate(3);
      Check(rate.Cost(4) == 12, "flat rate");
      Check(Total(rate, 0) == 0, "consumer uses contract");
    }
    Console.WriteLine("csharp-017: passed");
    await Task.CompletedTask;
  }

  public interface IRate {
    int Cost(int units);
  }
  public sealed record FlatRate(int Price) : IRate {
    public int Cost(int units) => checked(Price * units);
  }
  public sealed record CappedRate(int Price, int Cap) : IRate {
    public int Cost(int units) => Math.Min(checked(Price * units), Cap);
  }
  public static int Total(IRate rate, int units) => rate.Cost(units);
}
```

**Observe:** Four units cost 12 and zero units cost zero.

**Trace.** `rate` has static type `IRate` and refers to a `FlatRate` with Price 3. The call `rate.Cost(4)` dispatches to `FlatRate.Cost`, which returns 12. `Total(rate, 0)` accepts any `IRate`, calls `Cost(0)` through the interface and returns 0. Total never names FlatRate, so it would work unchanged with any other implementation, including one written after Total was compiled.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      IRate rate = new CappedRate(3, 10);
      Check(Total(rate, 4) == 10, "capped policy");
      Check(Total(new FlatRate(3), 4) == 12, "same consumer, different policy");
    }
    Console.WriteLine("csharp-017: passed");
    await Task.CompletedTask;
  }

  public interface IRate {
    int Cost(int units);
  }
  public sealed record FlatRate(int Price) : IRate {
    public int Cost(int units) => checked(Price * units);
  }
  public sealed record CappedRate(int Price, int Cap) : IRate {
    public int Cost(int units) => Math.Min(checked(Price * units), Cap);
  }
  public static int Total(IRate rate, int units) => rate.Cost(units);
}
```

**Observe:** The same consumer applies a capped or uncapped policy.

**Trace.** `CappedRate(3, 10).Cost(4)` computes 3 times 4, which is 12, then `Math.Min` returns the cap, 10. The second check passes a `FlatRate(3)` to the same `Total` method and gets the uncapped 12. One consumer, two policies: the runtime type of the argument chose which `Cost` body ran, and the consumer needed no `if` statement to pick a policy.

## Exercises

1. **Predict and explain.** Trace the interface call to the selected implementation.

2. **Guided modification.** Add a second flat rate and keep Total unchanged.

3. **Independent construction.** Define a small interface for a deterministic label formatter.

4. **Diagnose a defect.** Diagnose an implementation returning cents where the contract requires whole currency units.

5. **Boundary evidence.** Test zero and a value exactly at the cap.

6. **Transfer and justify.** Choose one dependency worth injecting in the inventory importer and explain the testing benefit.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.

For task 5, the exact-cap case needs a price times units that equals the cap, such as price 5 for 2 units under a cap of 10, which must return 10 whether `Min` keeps the product or the cap. For task 4, an implementation returning cents compiles against `IRate` and returns 1200 for four units, because a matching signature cannot check the unit.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use a declared contract) before changing anything, and confirm its observation: Four units cost 12 and zero units cost zero.
2. Compare Example B (Change policy without changing the consumer) with Example A and name the first line whose behavior differs. Its observation is: The same consumer applies a capped or uncapped policy.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Identical signatures do not imply compatible semantics.

## Self-check and next step

Explain which method body runs for `rate.Cost(4)` and what decides it. Give the cost of 0, 3 and 4 units under a cap of 10 with price 3. For task 6, name the dependency you would inject into the importer and describe the fake you would pass in tests.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): Interfaces are described in the C# reference and in the object-oriented programming tutorials, including explicit and default implementations.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
