# csharp-001: Source, compilation and the first observable result

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: None. Begin with the source file and visible result.

## Learning objectives

Build and run Program.cs and check a computed result instead of trusting printed text. The central exercise is task 3: Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly.

## Purpose and mental model

A program is text until a compiler translates it into a form the runtime can execute. In .NET, the SDK supplies build tools; the runtime loads managed code and supplies services such as allocation and exceptions. Installing only a runtime is insufficient for compiling new source. The classroom prepares the SDK inside Linux Docker, so the host browser does not need a C# compiler.

The first skill is distinguishing three outcomes: a compiler diagnostic means the program did not start; an exception means execution reached a failing operation; the expected printed result means a particular path completed. A message saying success proves nothing about an unchecked calculation. We therefore attach a small explicit condition to every reference and make false conditions terminate unsuccessfully.

## Vocabulary and concepts

**Source:** Human-readable program text.

**Compiler:** A tool that checks language rules and emits runnable managed code.

**Entrypoint:** The method the runtime calls to begin the program.

## How to run this lesson

Example A prints the greeting, while Example B prints nothing of its own, so the only line B adds to the output is the lesson marker. For task 4, delete one semicolon in a scratch copy: the build stops with CS1002 and no statement of the program runs.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`using System;` makes framework names available without their namespace prefix. `class Program` groups members. `static Main` is an entrypoint that needs no object instance. Braces delimit a body; a semicolon ends a statement. `Console.WriteLine` prints one line. The wrapper uses `async Task Main` to keep one entrypoint shape throughout the route; asynchronous work is explained later. For now, trace the statements from top to bottom.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: A checked greeting

The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture.

```csharp
using System;
using System.Threading.Tasks;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      string greeting = "Hello, C#";
      Check(greeting.Length == 9, "greeting length");
      Console.WriteLine(greeting);
    }
    Console.WriteLine("csharp-001: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Hello, C# appears before the lesson marker.

**Trace.** `greeting` is bound to the literal `"Hello, C#"`. Count its characters: H, e, l, l and o make five, the comma makes six, the space seven, and C and # bring it to nine. `Check` receives `greeting.Length == 9`, which is true, so it returns without throwing. Only then does `Console.WriteLine` print the greeting, so a wrong count stops the program before any output appears.

### Example B: A calculation instead of a hardcoded message

The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word.

```csharp
using System;
using System.Threading.Tasks;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int boxes = 3;
      int itemsPerBox = 4;
      int total = boxes * itemsPerBox;
      Check(total == 12, "computed total");
      Check(total != boxes + itemsPerBox, "multiplication is not addition");
    }
    Console.WriteLine("csharp-001: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The total is 12, while adding the two inputs gives 7.

**Trace.** `boxes` holds 3 and `itemsPerBox` holds 4. The expression `boxes * itemsPerBox` evaluates to 12, which is stored in `total`. The first check compares `total` with 12. The second compares it with `boxes + itemsPerBox`, which is 7, and requires the two to differ. If someone typed `+` instead of `*`, total would be 7 and the first check would throw with the reason computed total.

## Exercises

1. **Predict and explain.** Predict the greeting length, including its space and punctuation, before running Example A.

2. **Guided modification.** Change the greeting and update its independently counted expected length.

3. **Independent construction.** Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly.

4. **Diagnose a defect.** Temporarily remove a semicolon and classify the diagnostic as compilation rather than runtime failure. Restore it.

5. **Boundary evidence.** Compare zero rows with one row and explain why multiplication handles both without a branch.

6. **Transfer and justify.** Model boxes containing packets containing items. Explain each intermediate value and check the final product.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Printing a copied expected number skips the calculation. A missing brace can produce several later diagnostics, so repair the first structural problem before interpreting the rest. Do not treat the lesson marker as a replacement for inspecting the greeting or invariant.

Task 3's check `seats == 24` on its own is weak, because a hardcoded 24 also passes. Add the operator check from Example B: for four rows of six, the sum 10 must differ from the product. For task 5, zero rows give zero seats and one row gives six from the same formula. A missing closing brace is reported as CS1513 at the end of the file, far from where the brace belonged.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (A checked greeting) before changing anything, and confirm its observation: Hello, C# appears before the lesson marker.
2. Compare Example B (A calculation instead of a hardcoded message) with Example A and name the first line whose behavior differs. Its observation is: The total is 12, while adding the two inputs gives 7.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Printing a copied expected number skips the calculation.

## Self-check and next step

Without running anything, state the length of `"Hi, C#!"` and explain how you counted it. Explain why Example B's second check makes the program stronger evidence than printing 12. Classify a missing semicolon and a failed `Check` as compile or runtime failures, and say what output each one produces.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# documentation's tour of the language introduces program structure, the `Main` method and `Console.WriteLine`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-001: Source, compilation and the first observable result.
Read courses/csharp/guides/csharp-001.md and courses/csharp/lessons/csharp-001.cs. Prerequisites: none.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-001_solution.cs and
courses/csharp/solutions/csharp-001_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
