# csharp-046: Modern C# features and version-aware readability

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-045`

## Learning objectives

Refactor one simple class to a primary constructor without changing behavior. Then review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.

## Purpose and mental model

Language evolution adds concise ways to express familiar contracts. Primary constructors, collection expressions and improved patterns can reduce noise, but unfamiliar syntax should be introduced by its meaning rather than used to make code look advanced. Version-aware code records the target language generation and avoids accidentally relying on a preview feature.

C# 14 accompanies .NET 10. This chapter uses established modern features supported by that target and explains the broader C# 14 release boundary through official documentation. New syntax does not relax nullability, ownership or equality rules. A code review should ask whether a feature makes the domain relationship easier to see and whether contributors can diagnose its errors.

## Vocabulary and concepts

**Language version:** The set of syntax and semantic features accepted by the compiler.

**Target typing:** Using context to determine an expression type.

**Primary constructor:** Constructor parameters declared with a type definition.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A collection expression such as `[1, 2, 3]` is target-typed. A primary constructor supplies parameters used by members. `nameof` produces a symbol name while retaining compile-time refactoring support.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use a target-typed collection

The compact syntax still creates concrete storage according to its target.

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
      int[] values = [1, 2, 3];
      List<int> list = [..values, 4];
      Check(list.SequenceEqual(new[] { 1, 2, 3, 4 }), "collection spread");
    }
    Console.WriteLine("csharp-046: passed");
    await Task.CompletedTask;
  }

  public sealed class Scale(int factor) {
    public int Apply(int value) => checked(value * factor);
  }
}
```

**Observe:** The target types select array and list representations.

### Example B: Keep constructor policy visible

Concise construction should preserve a clear relationship between input parameters and behavior.

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
      var scale = new Scale(3);
      Check(scale.Apply(4) == 12, "primary constructor parameter");
      Check(nameof(Scale.Apply) == "Apply", "symbol name");
    }
    Console.WriteLine("csharp-046: passed");
    await Task.CompletedTask;
  }

  public sealed class Scale(int factor) {
    public int Apply(int value) => checked(value * factor);
  }
}
```

**Observe:** The supplied factor is used by the instance operation.

## Exercises

1. **Predict and explain.** Identify the target type of each collection expression.

2. **Guided modification.** Use an empty collection expression with an explicit target.

3. **Independent construction.** Refactor one simple class to a primary constructor without changing behavior.

4. **Diagnose a defect.** Diagnose copying new syntax into a project targeting an older language version.

5. **Boundary evidence.** Test empty spread and zero scaling.

6. **Transfer and justify.** Review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Language version, Target typing, Primary constructor without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-046: Modern C# features and version-aware readability.
Read courses/csharp/guides/csharp-046.md and courses/csharp/lessons/csharp-046.cs. Prerequisites: csharp-045.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-046_solution.cs and
courses/csharp/solutions/csharp-046_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
