# csharp-011: Nullability and optional information

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-010`

## Learning objectives

Represent missing information with nullable types and keep missing, zero and present values distinct. The central exercise is task 3: Write a formatter preserving missing, zero and positive measurements.

## Purpose and mental model

Missing information should be visible in a type and a control-flow policy. Nullable reference annotations let the compiler warn when a value may be null; they are static analysis, not a new runtime container. An annotation cannot validate data arriving from another language, reflection or an external format. Keep runtime validation where that data enters.

A nullable value type such as int? represents either an int or no value. Choosing a fallback is a domain decision. Replacing missing age with zero means something very different from reporting unknown age. Prefer explicit branches when a default would blur those meanings.

## Vocabulary and concepts

**Null:** A missing reference or absent nullable value.

**Flow analysis:** Compiler reasoning about possible values on each path.

**Fallback:** A deliberate replacement for absence.

## How to run this lesson

This lesson relies on the project's `<Nullable>enable</Nullable>` setting, which makes `string?` a checked annotation. Task 4's `label!.Length` on a null label compiles without any warning, because `!` suppresses it, and then throws `NullReferenceException` when it runs.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`string?` permits null in static analysis; `int?` is Nullable<int>. `?.` conditionally accesses a member and preserves absence. `??` supplies a fallback. The null-forgiving operator `!` silences analysis but performs no check.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `label` is null. `label?.Length` tests the receiver first and, finding null, skips the member access and produces null of type `int?`. The first check confirms that `length` is null rather than 0. `length ?? -1` substitutes -1 only at this display boundary, and `length` itself still says absent, so later code can still tell the two cases apart.

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

**Trace.** `measured` holds a present 0, so `HasValue` is true and `Value` is 0. `missing` has no value, so `HasValue` is false. In `Describe`, the pattern `value is int actual` matches only when a value is present and binds it to `actual`, an ordinary `int`. Zero becomes measured:0 and null becomes unknown, so the two cases never collapse into one string.

## Exercises

1. **Predict and explain.** Predict nullable length and its fallback for null and empty text.

2. **Guided modification.** Use a visible unknown label rather than a numeric sentinel.

3. **Independent construction.** Write a formatter preserving missing, zero and positive measurements.

4. **Diagnose a defect.** Diagnose using ! to suppress a warning on an actually null value.

5. **Boundary evidence.** Test whitespace-only text separately from null and empty text.

6. **Transfer and justify.** Design an import field whose missing value has different meaning from an explicit zero or empty value.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.

For task 5, use four inputs: null, empty text, three spaces and a real label. `string.IsNullOrEmpty` treats the first two alike, and `string.IsNullOrWhiteSpace` treats the first three alike, so pick the method that matches your contract. The tempting wrong fallback is `label?.Length ?? 0`, which reports a missing label as an empty one.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Carry absence through a computation) before changing anything, and confirm its observation: The optional length is absent, not zero.
2. Compare Example B (Distinguish zero from missing) with Example A and name the first line whose behavior differs. Its observation is: A measured zero and an unknown measurement produce distinct descriptions.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A warning suppression is not validation.

## Self-check and next step

Give the type and value of `label?.Length` when label is null and when it is empty text. Explain what `!` does at compile time and what it does at runtime. For task 6, write one import row in which a missing field, an explicit zero and an empty string each mean something different.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide's articles on nullable reference types and nullable value types explain annotations, warnings and `Nullable<T>`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
