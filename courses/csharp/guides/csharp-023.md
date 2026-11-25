# csharp-023: Exceptions and preserving failure meaning

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-022`

## Learning objectives

Throw and catch exceptions that keep invalid input, environment failures and their causes distinct. The central exercise is task 3: Define an import API with distinct invalid-input and storage-failure outcomes.

## Purpose and mental model

Exceptions carry an abnormal control-flow result across method boundaries. Catch an exception where the program can make a meaningful recovery decision, add context or translate it into a public error contract. Catching everything at every layer often destroys the reason the operation failed.

A normal absence can be represented without an exception when it is expected. A malformed argument or failed invariant should remain visible. When rethrowing in a catch block, use `throw;` to preserve the original stack relationship. When adding a domain exception, retain the original as InnerException. Logging the same exception at every layer can multiply noise without adding evidence.

## Vocabulary and concepts

**Exception:** An object describing abnormal completion.

**Stack trace:** The recorded call path associated with failure.

**Translation:** Mapping an internal failure to a public contract.

## How to run this lesson

`ParseCount` uses `CultureInfo.InvariantCulture`, which the worked examples import through `System.Globalization`, so the digits are read the same way on every machine. Text with digits too large for an int, such as 99999999999, throws `OverflowException` instead of `FormatException`, a third category for task 5.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`try` encloses an operation; typed catch selects a failure category; finally runs cleanup when control leaves the protected region. `throw;` rethrows the current exception. A catch filter with `when` narrows recovery policy.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Catch only the expected invalid format

The catch does not accidentally classify every possible programming error as bad user text.

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
      int ParseCount(string text) {
        int value = int.Parse(text, CultureInfo.InvariantCulture);
        if (value < 0)
          throw new ArgumentOutOfRangeException(nameof(text));
        return value;
      }
      bool format = false;
      try {
        ParseCount("oops");
      } catch (FormatException) {
        format = true;
      }
      Check(format && ParseCount("3") == 3, "format and success are distinct");
    }
    Console.WriteLine("csharp-023: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Malformed numeric text is caught as a format error.

**Trace.** `ParseCount("oops")` calls `int.Parse`, which throws `FormatException` because the text has no digits. The range check never runs. The catch filters on `FormatException` and sets `format` to true. `ParseCount("3")` parses 3, passes the range check and returns it, so both halves of the condition hold. A null argument would throw `ArgumentNullException`, which this catch deliberately does not handle.

### Example B: Retain an inner cause

A public description can add context without erasing the lower-level failure category.

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
      Exception? observed = null;
      try {
        try {
          throw new IOException("synthetic read failure");
        } catch (IOException cause) {
          throw new InvalidOperationException("import failed", cause);
        }
      } catch (InvalidOperationException error) {
        observed = error;
      }
      Check(observed?.InnerException is IOException, "cause retained");
    }
    Console.WriteLine("csharp-023: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The outer domain failure still contains the I/O cause.

**Trace.** The inner `try` throws an `IOException`. Its catch block wraps that exception as the inner exception of a new `InvalidOperationException` with the message import failed, and throws the wrapper. The outer catch stores it. `observed?.InnerException is IOException` is true, so the original cause survives inside the domain-level failure for anyone reading the logs.

## Exercises

1. **Predict and explain.** Identify which failure category each catch handles.

2. **Guided modification.** Add a separate negative-count case without classifying it as FormatException.

3. **Independent construction.** Define an import API with distinct invalid-input and storage-failure outcomes.

4. **Diagnose a defect.** Diagnose catch-all code that returns an empty successful report.

5. **Boundary evidence.** Test success, expected rejection and an unexpected exception separately.

6. **Transfer and justify.** Decide which layer owns user-facing error translation and which details should remain private diagnostics.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.

For task 2, `ParseCount("-1")` parses successfully and then throws `ArgumentOutOfRangeException`, so it must not land in the `FormatException` catch. Task 4's catch-all returning an empty report hides real failures; rethrow with a bare `throw;` when you cannot handle an exception, because `throw ex;` resets its stack trace.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Catch only the expected invalid format) before changing anything, and confirm its observation: Malformed numeric text is caught as a format error.
2. Compare Example B (Retain an inner cause) with Example A and name the first line whose behavior differs. Its observation is: The outer domain failure still contains the I/O cause.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A catch-all that returns a default can turn data loss into apparent success.

## Self-check and next step

Name the exception type `ParseCount` throws for oops, for -1, for 99999999999 and for empty text. Explain what the inner exception keeps that the outer message does not. For task 6, decide which layer turns exceptions into user messages and which details stay in logs.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide's exception handling articles describe `try`, `catch`, `finally`, exception filters and `InnerException`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-023: Exceptions and preserving failure meaning.
Read courses/csharp/guides/csharp-023.md and courses/csharp/lessons/csharp-023.cs. Prerequisites: csharp-022.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-023_solution.cs and
courses/csharp/solutions/csharp-023_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
