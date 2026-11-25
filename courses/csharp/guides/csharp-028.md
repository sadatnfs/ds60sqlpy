# csharp-028: Testing contracts with meaningful counterexamples

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-027`

## Learning objectives

Write table-driven tests with boundary cases that a plausible wrong implementation fails. The central exercise is task 3: Write table-driven checks for your inventory quantity validator.

## Purpose and mental model

A test is useful when a plausible wrong implementation would fail it. Repeating the implementation expression on both sides of an assertion provides weak independence. Start from a contract, choose a normal case, a boundary case and a known misconception, then derive expected outcomes separately.

The classroom uses framework-free throwing checks so the default route needs no package download. A separate prepared project can use a test framework and a test runner. Keep deterministic unit tests focused on pure behavior, and label integration tests that exercise files, databases or networks. A passing unit test does not prove a dependency is configured correctly.

## Vocabulary and concepts

**Test oracle:** The independent rule deciding whether behavior is correct.

**Regression case:** A case preserving evidence of a previous defect.

**Boundary test:** A test at a transition or limit of the contract.

## How to run this lesson

`ClampNonnegative` is declared after `Main`, and the test table in Example A is an array of named tuples. Each `Check` uses the same reason text, clamp contract, so if one row fails, print the row's input in your pad to find which case broke.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

A table of inputs and expected values separates cases from the loop executing them. An exception assertion should check the intended category. Avoid sleep-based timing tests; coordinate concurrent states with explicit signals.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Use independently derived cases

The literal expectations come from the stated clamp rule, not a duplicated implementation.

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
      var cases = new[] { (Input: -2, Expected: 0), (Input: 0, Expected: 0),
                          (Input: 3, Expected: 3) };
      foreach (var test in cases)
        Check(ClampNonnegative(test.Input) == test.Expected, "clamp contract");
    }
    Console.WriteLine("csharp-028: passed");
    await Task.CompletedTask;
  }

  public static int ClampNonnegative(int value) => value < 0 ? 0 : value;
}
```

**Observe:** Negative, zero and positive cases preserve their intended categories.

**Trace.** The table lists three cases whose expected values come from the rule itself: anything below zero becomes zero, and anything else stays. The loop passes -2 and expects 0, passes 0 and expects 0, and passes 3 and expects 3. Each row reflects a separate region of the input, so a mistake in any region breaks at least one row.

### Example B: Detect a plausible wrong function

A property complements examples but does not replace the domain-specific expected values.

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
      int Wrong(int value) => value <= 0 ? 1 : value;
      Check(Wrong(0) != ClampNonnegative(0), "boundary catches wrong default");
      Check(ClampNonnegative(ClampNonnegative(-4)) == ClampNonnegative(-4),
            "idempotence");
    }
    Console.WriteLine("csharp-028: passed");
    await Task.CompletedTask;
  }

  public static int ClampNonnegative(int value) => value < 0 ? 0 : value;
}
```

**Observe:** The zero case catches the incorrect default, and clamping twice changes nothing further.

**Trace.** `Wrong` returns 1 for zero, which looks plausible but breaks the rule. The first check confirms that the zero boundary separates it from the real function: 1 differs from 0. The second check applies a property: clamping -4 gives 0, and clamping 0 again still gives 0, so applying the function twice changes nothing.

## Exercises

1. **Predict and explain.** Explain which wrong implementations each case would reject.

2. **Guided modification.** Add an extreme integer case without overflow.

3. **Independent construction.** Write table-driven checks for your inventory quantity validator.

4. **Diagnose a defect.** Diagnose an assertion comparing a function call with the same call.

5. **Boundary evidence.** Test idempotence and an independently derived boundary value.

6. **Transfer and justify.** Separate unit and integration evidence for a JSON file importer.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Tests that always print success or catch their own assertion failures provide misleading evidence. A flaky test weakens trust even when production code is correct. Random generation requires a reproducible seed and a clear oracle.

For task 4, `Check(ClampNonnegative(x) == ClampNonnegative(x), ...)` passes for every implementation, including a wrong one, because it compares the function with itself. For task 2, `int.MinValue` must clamp to 0 and `int.MaxValue` must come back unchanged; neither needs arithmetic that could overflow.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use independently derived cases) before changing anything, and confirm its observation: Negative, zero and positive cases preserve their intended categories.
2. Compare Example B (Detect a plausible wrong function) with Example A and name the first line whose behavior differs. Its observation is: The zero case catches the incorrect default, and clamping twice changes nothing further.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Tests that always print success or catch their own assertion failures provide misleading evidence.

## Self-check and next step

Name one wrong implementation that each of the three table rows rejects. Explain why idempotence alone would accept a function that returns 0 for every input. For task 6, list which checks of a JSON importer run without touching the disk and which ones need a real file.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET testing documentation describes unit testing practices, test organization and naming that keep each case focused.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-028: Testing contracts with meaningful counterexamples.
Read courses/csharp/guides/csharp-028.md and courses/csharp/lessons/csharp-028.cs. Prerequisites: csharp-027.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-028_solution.cs and
courses/csharp/solutions/csharp-028_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
