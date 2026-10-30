# csharp-011: Nullability and optional information

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-010`

## Learning objectives

Write a formatter preserving missing, zero and positive measurements. Then design an import field whose missing value has different meaning from an explicit zero or empty value.

## Purpose and mental model

Missing information should be visible in a type and a control-flow policy. Nullable reference annotations let the compiler warn when a value may be null; they are static analysis, not a new runtime container. An annotation cannot validate data arriving from another language, reflection or an external format. Keep runtime validation where that data enters.

A nullable value type such as int? represents either an int or no value. Choosing a fallback is a domain decision. Replacing missing age with zero means something very different from reporting unknown age. Prefer explicit branches when a default would blur those meanings.

## Vocabulary and concepts

**Null:** A missing reference or absent nullable value.

**Flow analysis:** Compiler reasoning about possible values on each path.

**Fallback:** A deliberate replacement for absence.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`string?` permits null in static analysis; `int?` is Nullable<int>. `?.` conditionally accesses a member and preserves absence. `??` supplies a fallback. The null-forgiving operator `!` silences analysis but performs no check.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Carry absence through a computation

Conditional access propagates missing information until a boundary deliberately chooses a display representation.

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
      int? length = label?.Length;
      Check(length is null, "absence remains absent");
      Check((length ?? -1) == -1, "explicit display sentinel");
    }
    Console.WriteLine("csharp-011: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The optional length is absent, not zero.

### Example B: Distinguish zero from missing

Pattern matching unwraps only the present case, giving a nonnullable variable inside that branch.

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
      int? measured = 0;
      int? missing = null;
      Check(measured.HasValue && measured.Value == 0, "valid zero");
      Check(!missing.HasValue, "unknown measurement");
            string Describe(int? value) => value is int actual ? $"measured:{actual}" : "unknown";
            Check(Describe(measured) == "measured:0" &&
                      Describe(missing) == "unknown",
                  "preserved meaning");
    }
    Console.WriteLine("csharp-011: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** A measured zero and an unknown measurement produce distinct descriptions.

## Exercises

1. **Predict and explain.** Predict nullable length and its fallback for null and empty text.

2. **Guided modification.** Use a visible unknown label rather than a numeric sentinel.

3. **Independent construction.** Write a formatter preserving missing, zero and positive measurements.

4. **Diagnose a defect.** Diagnose using ! to suppress a warning on an actually null value.

5. **Boundary evidence.** Test whitespace-only text separately from null and empty text.

6. **Transfer and justify.** Design an import field whose missing value has different meaning from an explicit zero or empty value.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Null, Flow analysis, Fallback without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-011: Nullability and optional information.
Read courses/csharp/guides/csharp-011.md and courses/csharp/lessons/csharp-011.cs. Prerequisites: csharp-010.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-011_solution.cs and
courses/csharp/solutions/csharp-011_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
