# csharp-018: Generics and constraints that express capabilities

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-017`

## Learning objectives

Write generic types and methods whose constraints state exactly the capabilities they need. The central exercise is task 3: Create a generic immutable three-element container.

## Purpose and mental model

Generics let an algorithm or container retain a type relationship without copying source for each element type. A List<int> cannot accidentally accept text because the element relationship is checked by the compiler. This differs from storing everything as object and discovering type mistakes later through casts.

An unconstrained type parameter supports only operations valid for every possible type. Constraints declare additional capabilities, such as comparison or a required interface. The constraint should express what the algorithm really needs. A comparable type supports ordering, but the algorithm must still specify what happens for an empty sequence and whether ties preserve the first value.

## Vocabulary and concepts

**Type parameter:** A placeholder for a compile-time type.

**Constraint:** A requirement on admissible type arguments.

**Type safety:** Rejecting incompatible operations before execution.

## How to run this lesson

`Max` and `Pair<T>` are declared after `Main`; the call sites never write a type argument, because the compiler infers `T` from the arguments. For task 4, write a generic method with an unconstrained `T` that reads `.Length`; the compiler rejects it because nothing promises that member exists.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`T` names a type parameter. `where T : IComparable<T>` makes CompareTo available. The method call can infer T from its arguments. Return types preserve the relationship to the input type.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** In `Max(4, 9)` both arguments are `int`, so T is int, which implements `IComparable<int>`. `4.CompareTo(9)` is negative, so the method returns `right`, 9, typed as int. In `Max("apple", "pear")` T is string, the comparison is negative again and the result is pear, a string, with no cast needed. Each call site got its own closed method.

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

**Trace.** `new Pair<string>("left", "right")` stores two strings. `Swap()` returns a new `Pair<string>` with the fields exchanged, and record equality compares First and Second, so it equals the expected right, left pair. `Max(5, 5)` gets a CompareTo result of 0, which satisfies `>= 0`, so the method returns `left`. That tie rule is part of the method's observable contract.

## Exercises

1. **Predict and explain.** Predict the inferred type at each Max call.

2. **Guided modification.** Use Max with decimal values.

3. **Independent construction.** Create a generic immutable three-element container.

4. **Diagnose a defect.** Explain why an unconstrained T cannot safely call Length.

5. **Boundary evidence.** Test equal values and document whether the first or second object is returned on a tie.

6. **Transfer and justify.** Design a generic helper with the smallest useful capability constraint.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.

For task 5, ties return the left argument because the test is `>= 0`. With ints both arguments are equal, so test with records or objects whose comparison ignores one field. String comparison here is culture-aware; `string.CompareOrdinal("Pear", "pear")` is negative because P is code 80 and p is 112.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Retain the element type) before changing anything, and confirm its observation: The same method returns an int or a string without object casts.
2. Compare Example B (Preserve a generic relationship) with Example A and name the first line whose behavior differs. Its observation is: Swap preserves the element type, and a tie remains a valid value.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Adding a class constraint does not make arbitrary methods available.

## Self-check and next step

State the inferred T for `Max(2.5m, 1.5m)` and the value it returns. Explain why `where T : class` would not let `Max` call `CompareTo`. For task 6, write the smallest constraint your helper needs and name the operation that constraint makes available.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# reference on generic type parameters and on constraints on type parameters explains `where` clauses and type inference.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
