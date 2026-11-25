# csharp-002: Types, variables and explicit conversions

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-001`

## Learning objectives

Choose numeric types deliberately, convert explicitly and parse text with TryParse instead of exceptions. The central exercise is task 3: Write a TryParse-based validator accepting only nonnegative whole-number quantities.

## Purpose and mental model

A type describes the values an expression may hold and the operations available on those values. `int` represents a bounded whole number; `double` represents a binary floating-point approximation; `bool` represents a logical decision. A variable is a named storage location. Reassigning a variable changes its stored value, not its declared type.

`var` asks the compiler to infer a static type from the initializer. It does not make the variable dynamically typed. Conversions deserve attention because they can widen a range, lose fractional information, or fail. Put conversion at a visible boundary rather than scattering casts through a formula. First choose the meaning and units of the result, then choose its type.

## Vocabulary and concepts

**Static type:** The compile-time classification of an expression.

**Conversion:** A change from one type representation to another.

**Try pattern:** A Boolean success result paired with an output value.

## How to run this lesson

Both examples compile cleanly, so this lesson's surprises are runtime values rather than diagnostics. Task 1's third expression, `(double)(7/2)`, is worth running: it prints 3, not 3.5, because the cast happens after integer division has already discarded the half.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`int count = 7` declares and initializes. `var inferred = 7` also produces an int. `(double)count` converts before an operator uses the value. `int.TryParse(text, out int parsed)` returns success separately from the output value; a failed parse must not silently mean a real zero.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Division depends on operand types

Converting after integer division would preserve the already truncated result. Operand conversion must happen before division.

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
      int whole = 7 / 2;
      double fraction = (double)7 / 2;
      Check(whole == 3, "integer division");
      Check(fraction == 3.5, "floating division");
    }
    Console.WriteLine("csharp-002: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The integer result is 3 and the floating result is 3.5.

**Trace.** The literals 7 and 2 are both `int`, so `7 / 2` is integer division: the result 3 is stored in `whole` and the remainder is discarded. In the second line the cast binds tighter than division, so `(double)7` produces 7.0 first, and division between a double and an int converts the int, giving 3.5. The operand types chose the operation, not the variable on the left.

### Example B: Parse an external representation

The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value.

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
      bool accepted = int.TryParse("42", out int value);
      bool rejected = int.TryParse("forty-two", out _);
      Check(accepted && value == 42, "valid count");
      Check(!rejected, "invalid count is not zero");
    }
    Console.WriteLine("csharp-002: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** 42 parses successfully; words fail without an exception.

**Trace.** `int.TryParse("42", out int value)` reads the text, succeeds, writes 42 into `value` and returns true, which is stored in `accepted`. The second call receives forty-two spelled in words, fails, writes 0 into the discarded output and returns false. Neither call throws. The checks read the Boolean first, because the 0 written on failure is a placeholder rather than a parsed quantity.

## Exercises

1. **Predict and explain.** Predict the type and value of 7/2, 7/2.0 and (double)(7/2).

2. **Guided modification.** Change the operands to 8 and 2 and explain why that input hides the truncation difference.

3. **Independent construction.** Write a TryParse-based validator accepting only nonnegative whole-number quantities.

4. **Diagnose a defect.** Diagnose a conversion performed after integer division. Produce a fractional counterexample.

5. **Boundary evidence.** Test empty text, zero, a negative number and a number outside the int range.

6. **Transfer and justify.** Design an input boundary for a percentage and document its accepted textual and numeric ranges.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.

For task 3, `TryParse` returns true for -5, for `+5` and even for ` 42 ` with surrounding spaces, so a quantity validator needs a separate `parsed >= 0` condition. Text such as 3000000000 lies outside the int range and simply returns false. For task 4, the counterexample is 7 and 2: converting after division gives 3, while converting before gives 3.5.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Division depends on operand types) before changing anything, and confirm its observation: The integer result is 3 and the floating result is 3.5.
2. Compare Example B (Parse an external representation) with Example A and name the first line whose behavior differs. Its observation is: 42 parses successfully; words fail without an exception.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An inferred type is still static.

## Self-check and next step

State the type and value of `7 / 2.0` and of `(double)(7 / 2)`. Explain why `int.TryParse` returns a Boolean instead of returning 0 for bad text. List the inputs your quantity validator accepts and rejects, including empty text and a leading plus sign, and name the rule that rejects each one.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The language reference covers integral numeric types, explicit conversions and the arithmetic operators, including integer division.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-002: Types, variables and explicit conversions.
Read courses/csharp/guides/csharp-002.md and courses/csharp/lessons/csharp-002.cs. Prerequisites: csharp-001.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-002_solution.cs and
courses/csharp/solutions/csharp-002_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
