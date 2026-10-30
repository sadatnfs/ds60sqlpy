# csharp-018: Generics and constraints that express capabilities

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-017`

## Learning objectives

Create a generic immutable three-element container. Then design a generic helper with the smallest useful capability constraint.

## Purpose and mental model

Generics let an algorithm or container retain a type relationship without copying source for each element type. A List<int> cannot accidentally accept text because the element relationship is checked by the compiler. This differs from storing everything as object and discovering type mistakes later through casts.

An unconstrained type parameter supports only operations valid for every possible type. Constraints declare additional capabilities, such as comparison or a required interface. The constraint should express what the algorithm really needs. A comparable type supports ordering, but the algorithm must still specify what happens for an empty sequence and whether ties preserve the first value.

## Vocabulary and concepts

**Type parameter:** A placeholder for a compile-time type.

**Constraint:** A requirement on admissible type arguments.

**Type safety:** Rejecting incompatible operations before execution.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`T` names a type parameter. `where T : IComparable<T>` makes CompareTo available. The method call can infer T from its arguments. Return types preserve the relationship to the input type.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Retain the element type

The constraint guarantees comparison while the generic return preserves the concrete type.

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
      int larger = Max(4, 9);
      string later = Max("apple", "pear");
      Check(larger == 9 && later == "pear", "generic comparison");
    }
    Console.WriteLine("csharp-018: passed");
    await Task.CompletedTask;
  }

  public static T Max<T>(T left, T right)
      where T : IComparable<T> => left.CompareTo(right) >= 0 ? left : right;
  public record Pair<T>(T First, T Second) {
    public Pair<T> Swap() => new(Second, First);
  }
}
```

**Observe:** The same method returns an int or a string without object casts.

### Example B: Preserve a generic relationship

A generic data model encodes relationships between fields independently of the values used.

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
      var pair = new Pair<string>("left", "right");
      Check(pair.Swap() == new Pair<string>("right", "left"), "swapped pair");
      Check(Max(5, 5) == 5, "tie case");
    }
    Console.WriteLine("csharp-018: passed");
    await Task.CompletedTask;
  }

  public static T Max<T>(T left, T right)
      where T : IComparable<T> => left.CompareTo(right) >= 0 ? left : right;
  public record Pair<T>(T First, T Second) {
    public Pair<T> Swap() => new(Second, First);
  }
}
```

**Observe:** Swap preserves the element type, and a tie remains a valid value.

## Exercises

1. **Predict and explain.** Predict the inferred type at each Max call.

2. **Guided modification.** Use Max with decimal values.

3. **Independent construction.** Create a generic immutable three-element container.

4. **Diagnose a defect.** Explain why an unconstrained T cannot safely call Length.

5. **Boundary evidence.** Test equal values and document whether the first or second object is returned on a tie.

6. **Transfer and justify.** Design a generic helper with the smallest useful capability constraint.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Type parameter, Constraint, Type safety without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-018: Generics and constraints that express capabilities.
Read courses/csharp/guides/csharp-018.md and courses/csharp/lessons/csharp-018.cs. Prerequisites: csharp-017.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-018_solution.cs and
courses/csharp/solutions/csharp-018_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
