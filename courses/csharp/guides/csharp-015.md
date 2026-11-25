# csharp-015: Patterns and explicit state models

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-014`

## Learning objectives

Model explicit states with records and pattern matching so each state carries only its own data. The central exercise is task 3: Model a loading, ready and failed operation with separate payloads.

## Purpose and mental model

Pattern matching combines a test with structured access to the matched data. It can replace a chain of unsafe casts with branches that make the valid shape visible. Patterns are especially useful when a finite set of domain states carries different information, such as loading, success and failure. The goal is a truthful state model, not clever syntax.

A fallback branch should have a deliberate meaning. If a new domain state is introduced later, silently treating it as success is dangerous. C# class hierarchies are not fully closed algebraic data types, so review exhaustiveness and reject unexpected cases explicitly when necessary. Keep missing information distinct from failure information.

## Vocabulary and concepts

**Pattern:** A rule matching a value shape and optionally binding parts.

**Guard:** An additional condition on a matched case.

**State model:** A representation of allowed states and transitions.

## How to run this lesson

Example A declares `Describe` as a local function inside the example, while the `Result` hierarchy lives after `Main` as three record declarations. Task 4 is a compile-time lesson: putting an `object` arm first produces error CS8510 on the later arm, so the program never runs.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`value is int number` tests and binds. Property patterns inspect named properties. A switch expression can select an expression by type and guard. `when` adds a condition after the structural match.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Narrow before using a value

The bound number is available only after the type pattern succeeds.

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
      object value = 12;
      string Describe(object item) =>
          item switch { int number when number >
                            0 => "positive",
                        int => "nonpositive", string { Length : 0 } => "empty",
                        _ => "other" };
      Check(Describe(value) == "positive", "integer branch");
      Check(Describe(-1) == "nonpositive" && Describe("") == "empty",
            "distinct shapes");
    }
    Console.WriteLine("csharp-015: passed");
    await Task.CompletedTask;
  }

  public abstract record Result;
  public sealed record Success(int Count) : Result;
  public sealed record Failure(string Reason) : Result;
}
```

**Observe:** The same method distinguishes type, value range and string shape.

**Trace.** `value` holds a boxed 12. The switch tries `int number when number > 0`: the type test succeeds, binds 12 to `number`, and the guard passes, so the result is positive. For -1 the first arm's guard fails and the plain `int` arm returns nonpositive. Empty text skips both integer arms and matches the property pattern `string { Length: 0 }`.

### Example B: Represent results without impossible combinations

Separate cases prevent a Boolean success flag from disagreeing with unrelated optional fields.

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
      Result success = new Success(8);
      Result failure = new Failure("invalid");
      string Render(Result result) => result switch {
        Success(var count) => $"count:{count}",
        Failure(var reason) => $"error:{reason}",
        _ => throw new InvalidOperationException("unknown result")
      };
      Check(Render(success) == "count:8", "success payload");
      Check(Render(failure) == "error:invalid", "failure payload");
    }
    Console.WriteLine("csharp-015: passed");
    await Task.CompletedTask;
  }

  public abstract record Result;
  public sealed record Success(int Count) : Result;
  public sealed record Failure(string Reason) : Result;
}
```

**Observe:** Success carries a count; failure carries a reason.

**Trace.** `success` has static type `Result` and runtime type `Success`. In `Render`, the positional pattern `Success(var count)` checks the runtime type, deconstructs it and binds 8, so the result is count:8. `failure` fails that arm, matches `Failure(var reason)` and binds the reason text invalid. The discard arm throws because a third subtype would be a programming error.

## Exercises

1. **Predict and explain.** Predict the matched arm for zero, positive integer, empty text and nonempty text.

2. **Guided modification.** Add a nonempty string arm without shadowing the empty case.

3. **Independent construction.** Model a loading, ready and failed operation with separate payloads.

4. **Diagnose a defect.** Diagnose a broad object arm placed before a more specific case.

5. **Boundary evidence.** Test an unexpected subclass and explain the fallback policy.

6. **Transfer and justify.** Replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.

For task 4, an arm `object => "other"` placed first matches every non-null value, so the compiler rejects the later `int` arm with CS8510, the pattern is unreachable. Task 2's nonempty string arm must come after the empty case. In task 1, 0 falls to nonpositive and text like x lands on the discard arm.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Narrow before using a value) before changing anything, and confirm its observation: The same method distinguishes type, value range and string shape.
2. Compare Example B (Represent results without impossible combinations) with Example A and name the first line whose behavior differs. Its observation is: Success carries a count; failure carries a reason.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An early broad pattern can make a later case unreachable.

## Self-check and next step

Name the arm Example A's `Describe` selects for 0, 12, empty text and the text x. Explain what a `when` guard adds that a type pattern cannot express. For task 3, list the payload each of loading, ready and failed carries, and name one combination your design makes impossible.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The pattern matching overview in the C# documentation covers type, property, positional and relational patterns along with `when` guards.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-015: Patterns and explicit state models.
Read courses/csharp/guides/csharp-015.md and courses/csharp/lessons/csharp-015.cs. Prerequisites: csharp-014.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-015_solution.cs and
courses/csharp/solutions/csharp-015_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
