# csharp-012: Value copies, references and mutation ownership

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-011`

## Learning objectives

Predict copying and sharing for structs and classes and choose the right kind for a value or shared state. The central exercise is task 3: Choose a representation for a coordinate and for a shared session, explaining the difference.

## Purpose and mental model

Value and reference semantics describe what assignment copies. A value-type assignment copies the value. A reference-type assignment copies a reference, so both variables may reach the same object. This is more useful than the misleading slogan that values always live on the stack and objects always live on the heap: storage placement depends on context, while assignment semantics remain the reasoning tool.

A class can deliberately encapsulate mutation behind operations that preserve invariants. A value object can make independent copies easier to reason about. Neither choice is automatically faster or safer. Ask whether identity matters, whether consumers should share changes, and how large or expensive copies may become.

## Vocabulary and concepts

**Value semantics:** Assignment copies the represented value.

**Reference semantics:** Assignment copies a reference to shared identity.

**Ownership:** The responsibility for permitted mutation and lifetime.

## How to run this lesson

`Point` and `Counter` are helper types declared after `Main`, and both examples use them. Example A assigns the public field `X` directly; a struct with mutable public fields appears here only to make copying visible, not as a recommended design.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`struct` introduces a value type; `class` introduces a reference type. Assignment has the same spelling for both, so inspect the declared type. `ReferenceEquals` asks whether references identify the same object, not whether their properties happen to match.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Copy a value

The struct contains only integer fields, so its copied state is independently mutable.

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
      var first = new Point(2, 3);
      var second = first;
      second.X = 9;
      Check(first.X == 2 && second.X == 9, "struct copy");
    }
    Console.WriteLine("csharp-012: passed");
    await Task.CompletedTask;
  }

  public struct Point {
    public int X;
    public int Y;
    public Point(int x, int y) {
      X = x;
      Y = y;
    }
  }
  public sealed class Counter {
    public int Value { get; set; }
  }
}
```

**Observe:** Changing the copied point leaves the original X at 2.

**Trace.** `new Point(2, 3)` creates a value whose fields hold 2 and 3. `var second = first;` copies both fields into a separate value. Setting `second.X = 9` changes only that copy. The check reads `first.X` as 2 and `second.X` as 9: two variables, two independent sets of fields. No heap object is shared between them.

### Example B: Share an object identity

Passing or assigning a reference by value does not clone the referenced object.

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
      var first = new Counter();
      var second = first;
      second.Value++;
      Check(first.Value == 1, "shared mutation");
      Check(ReferenceEquals(first, second), "same object");
    }
    Console.WriteLine("csharp-012: passed");
    await Task.CompletedTask;
  }

  public struct Point {
    public int X;
    public int Y;
    public Point(int x, int y) {
      X = x;
      Y = y;
    }
  }
  public sealed class Counter {
    public int Value { get; set; }
  }
}
```

**Observe:** Both references observe the same counter increment.

**Trace.** `new Counter()` allocates one object whose `Value` is 0, and `first` stores a reference to it. `second = first` copies the reference, not the object. `second.Value++` reads 0 and writes 1 into the shared object, so `first.Value` also reads 1. `ReferenceEquals` returns true because both variables identify the same instance.

## Exercises

1. **Predict and explain.** Draw the values and references after each assignment.

2. **Guided modification.** Make a separate Counter instance and compare identity with equal property values.

3. **Independent construction.** Choose a representation for a coordinate and for a shared session, explaining the difference.

4. **Diagnose a defect.** Diagnose expecting assignment of a class variable to produce a deep copy.

5. **Boundary evidence.** Place a mutable list inside a struct and explain which part of the copied value remains shared.

6. **Transfer and justify.** Design a data boundary that prevents callers from mutating an internal collection.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.

For task 5, give `Point` a `List<int>` field: copying the struct copies the list reference, so an item added through one copy appears in the other. For task 2, two separate `Counter` objects with `Value` 1 are not `ReferenceEquals`, and because Counter does not override equality, `==` also compares references and returns false.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Copy a value) before changing anything, and confirm its observation: Changing the copied point leaves the original X at 2.
2. Compare Example B (Share an object identity) with Example A and name the first line whose behavior differs. Its observation is: Both references observe the same counter increment.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy.

## Self-check and next step

Draw boxes for `first` and `second` after each assignment in both examples and mark which ones share storage. Explain why equal property values do not imply the same object. For task 6, describe how your type hands out its internal list so that a caller cannot add to it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The reference articles on value types, reference types and equality comparisons separate copying, identity and equality.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-012: Value copies, references and mutation ownership.
Read courses/csharp/guides/csharp-012.md and courses/csharp/lessons/csharp-012.cs. Prerequisites: csharp-011.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-012_solution.cs and
courses/csharp/solutions/csharp-012_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
