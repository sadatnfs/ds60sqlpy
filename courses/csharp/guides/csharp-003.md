# csharp-003: Numeric range, checked overflow and decimal amounts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-002`

## Learning objectives

Detect integer overflow with checked arithmetic and calculate money with decimal and a named rounding rule. The central exercise is task 3: Calculate a decimal subtotal and tax, rounding only the final payable amount.

## Purpose and mental model

Arithmetic has representation limits. An `int` has a finite range, so mathematically valid addition may overflow. C# supports checked contexts that reject integral overflow and unchecked contexts that wrap. Neither behavior should be chosen accidentally for business quantities. Floating-point arithmetic instead approximates most decimal fractions, so equality of independently calculated doubles often needs a scale-aware tolerance.

Use `decimal` when a decimal representation matches the domain, such as many monetary calculations. Decimal arithmetic still has finite precision and range. Specify rounding at a business boundary, including its midpoint rule, rather than rounding every intermediate operation. Keep currency and units explicit: a bare number does not identify what it measures.

## Vocabulary and concepts

**Overflow:** A result outside the representation range.

**Decimal:** A base-ten-oriented finite precision numeric type.

**Rounding policy:** A rule selecting a representable result at a stated precision.

## How to run this lesson

Example A triggers an `OverflowException` on purpose and catches it, so a successful run has still exercised the failure path. Remove `checked` and nothing is thrown: the default unchecked context wraps `int.MaxValue + 1` to -2147483648, and the check then reports overflow must be visible.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`checked(expression)` asks for integral overflow detection in that expression. The `m` suffix selects decimal, while `0.1` defaults to double. `Math.Round(amount, 2, MidpointRounding.ToEven)` records both precision and tie policy.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Reject overflowing counts

The normal and failure paths separate an exceptional boundary from ordinary arithmetic.

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
      bool overflowed = false;
      try {
        int large = int.MaxValue;
        _ = checked(large + 1);
      } catch (OverflowException) {
        overflowed = true;
      }
      Check(overflowed, "overflow must be visible");
      Check(checked(100 + 20) == 120, "normal addition");
    }
    Console.WriteLine("csharp-003: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The maximum int plus one is rejected; 100 plus 20 is accepted.

**Trace.** `large` holds `int.MaxValue`, which is 2147483647. Inside `checked(...)`, adding 1 has no int representation, so the runtime throws `OverflowException` instead of wrapping. The catch block sets `overflowed` to true and the first check passes. Writing the literal `checked(int.MaxValue + 1)` fails to compile with CS0220, because the compiler evaluates constant expressions; the variable delays the overflow to runtime.

### Example B: Preserve decimal intent

A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation.

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
      decimal amount = 0.1m + 0.2m;
      Check(amount == 0.3m, "decimal tenths");
      Check(Math.Round(2.345m, 2, MidpointRounding.ToEven) == 2.34m,
            "even midpoint");
      Check(Math.Round(2.345m, 2, MidpointRounding.AwayFromZero) == 2.35m,
            "away midpoint");
    }
    Console.WriteLine("csharp-003: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Two valid midpoint policies produce 2.34 and 2.35.

**Trace.** `0.1m + 0.2m` adds two decimal values stored as base-ten digits, so the sum is exactly 0.3m and the equality holds. `Math.Round(2.345m, 2, MidpointRounding.ToEven)` sees the trailing 5 as an exact tie and moves to the even neighbor, 2.34. The same tie under `AwayFromZero` gives 2.35. Both are legitimate policies, which is why the call must name one.

## Exercises

1. **Predict and explain.** Predict which arithmetic operation throws and explain the representation boundary.

2. **Guided modification.** Replace maximum plus one with minimum minus one and check the failure.

3. **Independent construction.** Calculate a decimal subtotal and tax, rounding only the final payable amount.

4. **Diagnose a defect.** Diagnose a price parsed as double and later converted to decimal. Explain where approximation entered.

5. **Boundary evidence.** Compare midpoint values immediately below, at and above the rounding boundary.

6. **Transfer and justify.** Design a quantity and currency contract that states overflow, rounding and invalid-input behavior.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

`checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.

For task 5, use 2.3449m, 2.345m and 2.3451m: under `ToEven` they round to 2.34, 2.34 and 2.35, so only the exact midpoint reveals the policy. For task 4, `(decimal)(0.1 + 0.2)` prints 0.3 here because the conversion keeps about 15 significant digits, so the approximation can hide. Parse money text with `decimal.Parse` from the start.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Reject overflowing counts) before changing anything, and confirm its observation: The maximum int plus one is rejected; 100 plus 20 is accepted.
2. Compare Example B (Preserve decimal intent) with Example A and name the first line whose behavior differs. Its observation is: Two valid midpoint policies produce 2.34 and 2.35.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: `checked` does not turn floating-point arithmetic into exact decimal arithmetic.

## Self-check and next step

Explain why `checked(large + 1)` throws while `large + 1` alone does not. Round 2.345m and 2.355m to two places under both midpoint policies and give all four results. Describe one invoice where rounding each line item first gives a different total from rounding only the final sum.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The reference pages for the `checked` and `unchecked` statements and for floating-point numeric types explain overflow contexts and decimal precision.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-003: Numeric range, checked overflow and decimal amounts.
Read courses/csharp/guides/csharp-003.md and courses/csharp/lessons/csharp-003.cs. Prerequisites: csharp-002.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-003_solution.cs and
courses/csharp/solutions/csharp-003_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
