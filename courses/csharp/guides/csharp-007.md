# csharp-007: Methods, parameters and return contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-006`

## Learning objectives

Write a method computing an area from validated nonnegative dimensions. Then extract one computation from a larger program and state its input, output, mutation and failure contract.

## Purpose and mental model

A method gives a computation a name and a boundary. Its contract states accepted inputs, its result, state changes and failure behavior. Splitting code into methods helps only when those boundaries expose meaning. A helper that secretly edits unrelated state is harder to reason about than one returning a clearly defined result.

C# normally passes arguments by value. For a value type, that means a copied value; for an object reference, it means a copied reference to the same object. The distinction becomes important later. Start with small pure methods, which depend only on arguments and return a result without observable mutation. They are easy to test because the same inputs produce the same outputs.

## Vocabulary and concepts

**Parameter:** A named input in a method definition.

**Argument:** The value supplied at a call site.

**Pure function:** A computation without observable external mutation.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`int Double(int value) => value * 2` declares a local function with a typed parameter and return. `return` ends the current method. `ref` and `out` are explicit parameter passing modes, not decorations; prefer ordinary return values until shared mutation is required.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Trace the caller and parameter values through Double.

2. **Guided modification.** Add a Triple function and test zero and a negative input.

3. **Independent construction.** Write a method computing an area from validated nonnegative dimensions.

4. **Diagnose a defect.** Diagnose a function whose name promises exact division but silently truncates.

5. **Boundary evidence.** Test zero divisors and non-divisible inputs separately.

6. **Transfer and justify.** Extract one computation from a larger program and state its input, output, mutation and failure contract.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A method name is part of the interface. A generic catch returning zero can make rejected input indistinguishable from a valid zero result. Prefer one clear responsibility over a long list of optional switches.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Parameter, Argument, Pure function without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
