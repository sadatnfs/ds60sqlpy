# csharp-046: Modern C# features and version-aware readability

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-045`

## Learning objectives

Use C# 12 to 14 features such as collection expressions, primary constructors and null-conditional assignment where they make code clearer. The central exercise is task 3: Refactor one simple class to a primary constructor without changing behavior.

## Purpose and mental model

Language evolution adds concise ways to express familiar contracts. Primary constructors, collection expressions and improved patterns can reduce noise, but unfamiliar syntax should be introduced by its meaning rather than used to make code look advanced. Version-aware code records the target language generation and avoids accidentally relying on a preview feature.

C# 14 accompanies .NET 10 and is the default for the classroom's net10.0 target. C# 13 (.NET 9) added params collections, the System.Threading.Lock type for lock statements and the \e escape sequence. C# 14 adds the field keyword in property accessors, extension members, null-conditional assignment such as a?.B = c, nameof for unbound generic types such as List<> and implicit span conversions. Example B exercises three of these features. New syntax does not relax nullability, ownership or equality rules. A code review should ask whether a feature makes the domain relationship easier to see and whether contributors can diagnose its errors.

## Vocabulary and concepts

**Language version:** The set of syntax and semantic features accepted by the compiler.

**Target typing:** Using context to determine an expression type.

**Primary constructor:** Constructor parameters declared with a type definition.

## How to run this lesson

The net10.0 target selects C# 14 by default, which this lesson needs. Rebuilding the same file with `LangVersion` set to 12 fails with CS9202 for `nameof(List<>)`, and the message names version 14. A bare `var x = [];` fails at any version with CS9176, because a collection expression needs a target type.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

A collection expression such as `[1, 2, 3]` is target-typed. A primary constructor supplies parameters used by members. `nameof` produces a symbol name while retaining compile-time refactoring support; since C# 14 it also accepts an unbound generic type such as `nameof(List<>)`. `missing?.Capacity = 32` assigns only when `missing` is not null, and `\e` is the escape character U+001B.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `int[] values = [1, 2, 3];` builds an array because the declared type is `int[]`. `List<int> list = [.. values, 4];` creates a list, copies the three elements through the spread `..`, then adds 4. `SequenceEqual` compares positions one by one and finds 1, 2, 3, 4. The same bracket syntax produced two different concrete types.

### Example B: Keep constructor policy visible

Concise construction should preserve a clear relationship between input parameters and behavior. The three newer checks compile only with C# 13 or 14, which the net10.0 target selects by default; an older target would reject them at compile time.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            var scale = new Scale(3);
            Check(scale.Apply(4) == 12, "primary constructor parameter");
            Check(nameof(List<>) == "List", "C# 14 unbound generic nameof");
            StringBuilder? missing = null;
            missing?.Capacity = 32;
            Check(missing is null, "C# 14 null-conditional assignment");
            Check("\e" == "\u001b", "C# 13 escape sequence");
        }
        Console.WriteLine("csharp-046: passed");
        await Task.CompletedTask;
    }

    public sealed class Scale(int factor) { public int Apply(int value) => checked(value * factor); }
}
```

**Observe:** The supplied factor is used by the instance operation, nameof(List<>) is List, missing?.Capacity = 32 leaves the null builder alone, and \e is the escape character.

**Trace.** `Scale(3)` captures `factor` as 3, and `Apply(4)` returns the checked product 12. `nameof(List<>)` yields List with no type argument. `missing?.Capacity = 32` evaluates `missing`, finds null and skips the assignment, so no exception occurs. `\e` and `\u001b` both denote the escape character, so the two strings compare equal and the final check passes.

## Exercises

1. **Predict and explain.** Identify the target type of each collection expression.

2. **Guided modification.** Use an empty collection expression with an explicit target.

3. **Independent construction.** Refactor one simple class to a primary constructor without changing behavior.

4. **Diagnose a defect.** Diagnose copying new syntax into a project targeting an older language version.

5. **Boundary evidence.** Test empty spread and zero scaling.

6. **Transfer and justify.** Review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.

For task 5, an empty spread such as `[.. Array.Empty<int>()]` gives an empty list, and `Scale(0).Apply(5)` returns 0. `Scale(int.MaxValue).Apply(2)` throws `OverflowException` because `Apply` multiplies inside `checked`. For task 4, the CS9202 message names the required version; raise it deliberately or keep the older syntax.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use a target-typed collection) before changing anything, and confirm its observation: The target types select array and list representations.
2. Compare Example B (Keep constructor policy visible) with Example A and name the first line whose behavior differs. Its observation is: The supplied factor is used by the instance operation, nameof(List<>) is List, missing?.Capacity = 32 leaves the null builder alone, and \e is the escape character.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Newer syntax is not inherently better.

## Self-check and next step

Name the concrete type each collection expression creates in Example A. Explain what the null-conditional assignment does when `missing` refers to a real builder. For task 6, judge one newer feature by three tests: whether the team's target framework compiles it, whether readers recognize it, and whether tooling formats it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14): What's new in C# 14 lists the unbound generic `nameof`, null-conditional assignment and the other features available to net10.0 projects.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
