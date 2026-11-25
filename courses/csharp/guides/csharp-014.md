# csharp-014: Records, structs and data equality

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-013`

## Learning objectives

Use records and structs for value equality and explain what a shallow with-copy shares. The central exercise is task 3: Design an immutable coordinate using a readonly record struct.

## Purpose and mental model

Records describe data with synthesized equality and convenient copying. A record class still has reference identity, but its equality normally compares declared data members. A record struct is a value type. These features reduce boilerplate; they do not automatically make nested objects immutable or define the correct business identity.

A with expression constructs a copy with selected changes. That copy is shallow for referenced members. When a record contains a mutable list, two record instances may still share that list. Use immutable representations or deliberate copying when independent history is required. Choose equality fields from the domain rather than accepting every field merely because generation is convenient.

## Vocabulary and concepts

**Record:** A data-focused type with synthesized equality members.

**With expression:** A copy with selected member changes.

**Shallow copy:** A copy that retains references to nested objects.

## How to run this lesson

Both record types are one-line declarations placed after `Main`. Run task 1 before reading the output, because the two checks in Example A ask different questions: `==` compares the generated value equality, while `ReferenceEquals` asks whether two variables name the same object.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`record Person(string Name, int Age)` declares positional properties and value-based equality. `record struct` changes assignment semantics. `with { Age = 31 }` creates a changed copy. `==` on records follows generated value equality.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Equal data with distinct identities

Value equality and reference identity answer different questions.

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
      var first = new Person("Ada", 30);
      var second = new Person("Ada", 30);
      Check(first == second, "record value equality");
      Check(!ReferenceEquals(first, second), "distinct objects");
      var older = first with { Age = 31 };
      Check(first.Age == 30 && older.Age == 31, "copy retains prior value");
    }
    Console.WriteLine("csharp-014: passed");
    await Task.CompletedTask;
  }

  public record Person(string Name, int Age);
  public record Basket(List<int> Items);
}
```

**Observe:** Equal records can be distinct objects; with preserves the previous age.

**Trace.** `first` and `second` are built from the same arguments, so the compiler-generated equality compares Name and Age and `==` returns true. They are still two allocations, so `ReferenceEquals` returns false. `first with { Age = 31 }` copies every property into a new record and then sets Age, so `first.Age` stays 30 while `older.Age` is 31.

### Example B: Notice nested shared state

The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise.

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
      var first = new Basket(new List<int> { 1 });
      var second = first with {};
      second.Items.Add(2);
      Check(first.Items.Count == 2, "nested list is shared");
      Check(ReferenceEquals(first.Items, second.Items),
            "shallow copied member");
    }
    Console.WriteLine("csharp-014: passed");
    await Task.CompletedTask;
  }

  public record Person(string Name, int Age);
  public record Basket(List<int> Items);
}
```

**Observe:** Both records see the appended list item.

**Trace.** `first` holds a `Basket` whose Items property refers to a list containing 1. `first with { }` copies the property value, which is that list reference, into a new record. `second.Items.Add(2)` mutates the one shared list, so `first.Items.Count` becomes 2 and `ReferenceEquals(first.Items, second.Items)` is true. The `with` expression made a shallow copy.

## Exercises

1. **Predict and explain.** Predict record equality and reference equality separately.

2. **Guided modification.** Create a changed copy with a new name and retain the original.

3. **Independent construction.** Design an immutable coordinate using a readonly record struct.

4. **Diagnose a defect.** Diagnose a supposedly immutable history entry containing a mutable list.

5. **Boundary evidence.** Compare records whose nested collections contain equal values but have different identities.

6. **Transfer and justify.** Choose identity-based or data-based equality for an order and explain how updates affect collection membership.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.

For task 5, two baskets built from separate lists that each contain 1 compare unequal: the generated equality compares the Items references, not the list contents. For task 3, a `readonly record struct Coord(int X, int Y)` with value 1, 2 and a copy `with { X = 5 }` leaves the original at 1, 2, and its properties cannot be assigned afterward.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Equal data with distinct identities) before changing anything, and confirm its observation: Equal records can be distinct objects; with preserves the previous age.
2. Compare Example B (Notice nested shared state) with Example A and name the first line whose behavior differs. Its observation is: Both records see the appended list item.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Record equality does not recursively compare arbitrary collection contents.

## Self-check and next step

Predict `==` and `ReferenceEquals` for two `Person` records holding the same name and age. Explain why `with` cannot isolate a nested list. For task 6, decide whether an order with a changing status should use identity or data equality while it sits in a `HashSet`, and justify the choice.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The language reference article on records describes positional syntax, value equality, `with` expressions and record structs.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-014: Records, structs and data equality.
Read courses/csharp/guides/csharp-014.md and courses/csharp/lessons/csharp-014.cs. Prerequisites: csharp-013.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-014_solution.cs and
courses/csharp/solutions/csharp-014_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
