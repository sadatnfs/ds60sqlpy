# csharp-015: Patterns and explicit state models

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-014`

## Learning objectives

Model a loading, ready and failed operation with separate payloads. Then replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.

## Purpose and mental model

Pattern matching combines a test with structured access to the matched data. It can replace a chain of unsafe casts with branches that make the valid shape visible. Patterns are especially useful when a finite set of domain states carries different information, such as loading, success and failure. The goal is a truthful state model, not clever syntax.

A fallback branch should have a deliberate meaning. If a new domain state is introduced later, silently treating it as success is dangerous. C# class hierarchies are not fully closed algebraic data types, so review exhaustiveness and reject unexpected cases explicitly when necessary. Keep missing information distinct from failure information.

## Vocabulary and concepts

**Pattern:** A rule matching a value shape and optionally binding parts.

**Guard:** An additional condition on a matched case.

**State model:** A representation of allowed states and transitions.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`value is int number` tests and binds. Property patterns inspect named properties. A switch expression can select an expression by type and guard. `when` adds a condition after the structural match.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Predict the matched arm for zero, positive integer, empty text and nonempty text.

2. **Guided modification.** Add a nonempty string arm without shadowing the empty case.

3. **Independent construction.** Model a loading, ready and failed operation with separate payloads.

4. **Diagnose a defect.** Diagnose a broad object arm placed before a more specific case.

5. **Boundary evidence.** Test an unexpected subclass and explain the fallback policy.

6. **Transfer and justify.** Replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Pattern, Guard, State model without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
