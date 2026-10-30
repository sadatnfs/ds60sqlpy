# csharp-001: Source, compilation and the first observable result

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: None. Begin with the source file and visible result.

## Learning objectives

Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly. Then model boxes containing packets containing items. Explain each intermediate value and check the final product.

## Purpose and mental model

A program is text until a compiler translates it into a form the runtime can execute. In .NET, the SDK supplies build tools; the runtime loads managed code and supplies services such as allocation and exceptions. Installing only a runtime is insufficient for compiling new source. The classroom prepares the SDK inside Linux Docker, so the host browser does not need a C# compiler.

The first skill is distinguishing three outcomes: a compiler diagnostic means the program did not start; an exception means execution reached a failing operation; the expected printed result means a particular path completed. A message saying success proves nothing about an unchecked calculation. We therefore attach a small explicit condition to every reference and make false conditions terminate unsuccessfully.

## Vocabulary and concepts

**Source:** Human-readable program text.

**Compiler:** A tool that checks language rules and emits runnable managed code.

**Entrypoint:** The method the runtime calls to begin the program.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`using System;` makes framework names available without their namespace prefix. `class Program` groups members. `static Main` is an entrypoint that needs no object instance. Braces delimit a body; a semicolon ends a statement. `Console.WriteLine` prints one line. The wrapper uses `async Task Main` to keep one entrypoint shape throughout the route; asynchronous work is explained later. For now, trace the statements from top to bottom.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: A checked greeting

The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture.

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

### Example B: A calculation instead of a hardcoded message

The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word.

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

## Exercises

1. **Predict and explain.** Predict the greeting length, including its space and punctuation, before running Example A.

2. **Guided modification.** Change the greeting and update its independently counted expected length.

3. **Independent construction.** Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly.

4. **Diagnose a defect.** Temporarily remove a semicolon and classify the diagnostic as compilation rather than runtime failure. Restore it.

5. **Boundary evidence.** Compare zero rows with one row and explain why multiplication handles both without a branch.

6. **Transfer and justify.** Model boxes containing packets containing items. Explain each intermediate value and check the final product.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Printing a copied expected number skips the calculation. A missing brace can produce several later diagnostics, so repair the first structural problem before interpreting the rest. Do not treat the lesson marker as a replacement for inspecting the greeting or invariant.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Source, Compiler, Entrypoint without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
