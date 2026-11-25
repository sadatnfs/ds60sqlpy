# csharp-007: Methods, parameters and return contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-006`

## Learning objectives

Write methods with validated parameters and explicit return contracts that reject invalid input. The central exercise is task 3: Write a method computing an area from validated nonnegative dimensions.

## Purpose and mental model

A method gives a computation a name and a boundary. Its contract states accepted inputs, its result, state changes and failure behavior. Splitting code into methods helps only when those boundaries expose meaning. A helper that secretly edits unrelated state is harder to reason about than one returning a clearly defined result.

C# normally passes arguments by value. For a value type, that means a copied value; for an object reference, it means a copied reference to the same object. The distinction becomes important later. Start with small pure methods, which depend only on arguments and return a result without observable mutation. They are easy to test because the same inputs produce the same outputs.

## Vocabulary and concepts

**Parameter:** A named input in a method definition.

**Argument:** The value supplied at a call site.

**Pure function:** A computation without observable external mutation.

## How to run this lesson

`Double` and `DivideExact` are local functions declared inside their example blocks, so each example compiles on its own. `Double` multiplies inside `checked`, so `Double(int.MaxValue)` throws `OverflowException` instead of returning a negative number; try it while you write task 2's cases.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`int Double(int value) => value * 2` declares a local function with a typed parameter and return. `return` ends the current method. `ref` and `out` are explicit parameter passing modes, not decorations; prefer ordinary return values until shared mutation is required.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Return a transformed value

The parameter receives a value. Returning a transformed value does not reassign the caller variable.

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
      int Double(int value) => checked(value * 2);
      int original = 7;
      int result = Double(original);
      Check(result == 14 && original == 7, "input value is retained");
      Check(Double(0) == 0, "zero case");
    }
    Console.WriteLine("csharp-007: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The result is 14 and the caller still holds 7.

**Trace.** `original` holds 7. The call `Double(original)` copies 7 into the parameter `value`. The function multiplies inside `checked` and returns 14, which is stored in `result`. Nothing assigns to `original`, and the parameter was a separate copy, so the caller's variable still holds 7. The second check runs `Double(0)` to show that zero needs no special handling.

### Example B: Expose rejection as part of the contract

A precise function name and guard prevent accidental truncation from masquerading as a valid result.

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
      int DivideExact(int value, int divisor) {
        if (divisor == 0 || value % divisor != 0)
          throw new ArgumentException("exact nonzero divisor required");
        return value / divisor;
      }
      Check(DivideExact(12, 3) == 4, "exact quotient");
      bool rejected = false;
      try {
        _ = DivideExact(7, 2);
      } catch (ArgumentException) {
        rejected = true;
      }
      Check(rejected, "fractional quotient rejected");
    }
    Console.WriteLine("csharp-007: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** 12 divided by 3 returns 4; the exact-integer contract rejects 7 divided by 2.

**Trace.** For 12 and 3, the guard tests `divisor == 0`, which is false, then `12 % 3 != 0`, also false, so the method returns 4. For 7 and 2 the remainder is 1, so the guard throws `ArgumentException` and the catch sets `rejected`. Because `||` short-circuits, a zero divisor is rejected before `%` runs, so the method never throws `DivideByZeroException`.

## Exercises

1. **Predict and explain.** Trace the caller and parameter values through Double.

2. **Guided modification.** Add a Triple function and test zero and a negative input.

3. **Independent construction.** Write a method computing an area from validated nonnegative dimensions.

4. **Diagnose a defect.** Diagnose a function whose name promises exact division but silently truncates.

5. **Boundary evidence.** Test zero divisors and non-divisible inputs separately.

6. **Transfer and justify.** Extract one computation from a larger program and state its input, output, mutation and failure contract.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A method name is part of the interface. A generic catch returning zero can make rejected input indistinguishable from a valid zero result. Prefer one clear responsibility over a long list of optional switches.

Task 4's tempting wrong version returns `value / divisor` without the remainder test, so 7 and 2 quietly return 3. Task 5 needs separate cases because the failures have different causes: 5 and 0 must reject on the divisor test, while 7 and 2 reject on the remainder test. Swapping the guard's operands turns the zero case into a `DivideByZeroException`.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Return a transformed value) before changing anything, and confirm its observation: The result is 14 and the caller still holds 7.
2. Compare Example B (Expose rejection as part of the contract) with Example A and name the first line whose behavior differs. Its observation is: 12 divided by 3 returns 4; the exact-integer contract rejects 7 divided by 2.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A method name is part of the interface.

## Self-check and next step

Trace `original`, `value` and `result` through the call `Double(original)`. Explain why `DivideExact` throws rather than returning 0 for 7 and 2. For task 3's area method, list each rejected input, the exception type you throw and the message a caller would read.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# programming guide covers methods, local functions, parameters and the `ref` and `out` modifiers.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-007: Methods, parameters and return contracts.
Read courses/csharp/guides/csharp-007.md and courses/csharp/lessons/csharp-007.cs. Prerequisites: csharp-006.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-007_solution.cs and
courses/csharp/solutions/csharp-007_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
