# csharp-005: Boolean decisions and exhaustive alternatives

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-004`

## Learning objectives

Write complete, non-overlapping decisions with if statements and switch expressions, including boundary values. The central exercise is task 3: Write a classifier for negative, zero and positive temperatures.

## Purpose and mental model

A branch chooses one path based on a Boolean expression. Good branches expose the domain distinction, not just a compact operator chain. Short-circuit operators evaluate their right side only when needed, which lets a guard protect a later operation. This is a control-flow property, not merely a performance optimization.

For mutually exclusive categories, put the cases in an order that matches the domain and include a policy for values outside the range. A boundary such as zero should have a deliberate meaning. Testing values just below, exactly at and just above a threshold detects mistakes that a typical middle value will miss.

## Vocabulary and concepts

**Predicate:** An expression producing true or false.

**Short circuit:** Skipping an unnecessary right-hand expression.

**Boundary:** An input where a classification changes.

## How to run this lesson

With nullable analysis on, Example A compiles without warnings because the compiler follows the `label != null` test across `&&`. Task 4's version using `&` compiles with warning CS8602 and, when label is null, throws `NullReferenceException`, so you see the static warning and the runtime failure together.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`&&` requires both conditions and stops after false; `||` stops after true. A switch expression returns one value from its matching arm. The discard pattern `_` can provide an explicit fallback but must not conceal invalid input.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: A guard prevents unsafe access

The left operand establishes the precondition needed by the right operand.

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
      string? label = null;
      Check(!(label != null && label.Length > 0), "guarded access");
      label = "ok";
      Check(label != null && label.Length == 2, "present label");
    }
    Console.WriteLine("csharp-005: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The missing value is handled without dereferencing null.

**Trace.** With `label` null, `label != null` is false. `&&` stops there, so `label.Length` never runs, the whole condition is false and the negated check passes. After `label = "ok"`, the left operand is true, so the right operand runs: Length is 2 and the second check passes. The order of the operands is what makes the guard work.

### Example B: Classify a threshold

Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category.

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
      string Classify(int score) => score switch { <
                                                       0 => "invalid",
                                                   <
                                                       60 => "retry",
                                                   <=
                                                       100 => "pass",
                                                   _ => "invalid" };
      Check(Classify(59) == "retry", "below boundary");
      Check(Classify(60) == "pass", "at boundary");
      Check(Classify(101) == "invalid", "outside domain");
    }
    Console.WriteLine("csharp-005: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** 59 retries, 60 passes, and 101 is rejected.

**Trace.** The switch expression tests its arms from top to bottom and returns the first match. For 59, `< 0` fails and `< 60` matches, giving retry. For 60, `< 60` fails and `<= 100` matches, giving pass. For 101, every relational arm fails and the discard `_` returns invalid. Because the arms are ordered, each one needs only its upper bound.

## Exercises

1. **Predict and explain.** Trace which operands execute when label is null.

2. **Guided modification.** Change the classifier pass threshold to 70 and update boundary checks.

3. **Independent construction.** Write a classifier for negative, zero and positive temperatures.

4. **Diagnose a defect.** Find why replacing && with & can break a null guard.

5. **Boundary evidence.** Test the two ends of the valid score range and one value beyond each end.

6. **Transfer and justify.** Choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.

The boundary set for task 5 is -1, 0, 100 and 101: -1 and 101 must be invalid, 0 is retry and 100 is pass. A tempting wrong version drops the `< 0` arm, so -1 becomes retry and a corrupt score asks the student to try again. For task 2, moving the threshold to 70 makes 69 and 70 the new pair to check.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (A guard prevents unsafe access) before changing anything, and confirm its observation: The missing value is handled without dereferencing null.
2. Compare Example B (Classify a threshold) with Example A and name the first line whose behavior differs. Its observation is: 59 retries, 60 passes, and 101 is rejected.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An else branch can accidentally classify every invalid value as valid.

## Self-check and next step

Trace which operands run for `label != null && label.Length > 0` when label is null and when it is empty. Predict what the compiler reports if the `<= 100` arm is moved above `< 60`; it is error CS8510, an unreachable arm. Describe how your temperature classifier represents a reading that is not a number at all.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The reference articles on Boolean logical operators and on the switch expression describe short-circuit evaluation and relational patterns.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-005: Boolean decisions and exhaustive alternatives.
Read courses/csharp/guides/csharp-005.md and courses/csharp/lessons/csharp-005.cs. Prerequisites: csharp-004.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-005_solution.cs and
courses/csharp/solutions/csharp-005_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
