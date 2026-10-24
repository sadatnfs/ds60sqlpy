# csharp-023: Exceptions and preserving failure meaning

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-022`

## Learning objectives

Define an import API with distinct invalid-input and storage-failure outcomes. Then decide which layer owns user-facing error translation and which details should remain private diagnostics.

## Purpose and mental model

Exceptions carry an abnormal control-flow result across method boundaries. Catch an exception where the program can make a meaningful recovery decision, add context or translate it into a public error contract. Catching everything at every layer often destroys the reason the operation failed.

A normal absence can be represented without an exception when it is expected. A malformed argument or failed invariant should remain visible. When rethrowing in a catch block, use `throw;` to preserve the original stack relationship. When adding a domain exception, retain the original as InnerException. Logging the same exception at every layer can multiply noise without adding evidence.

## Vocabulary and concepts

**Exception:** An object describing abnormal completion.

**Stack trace:** The recorded call path associated with failure.

**Translation:** Mapping an internal failure to a public contract.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`try` encloses an operation; typed catch selects a failure category; finally runs cleanup when control leaves the protected region. `throw;` rethrows the current exception. A catch filter with `when` narrows recovery policy.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            int ParseCount(string text) { int value = int.Parse(text, CultureInfo.InvariantCulture); if (value < 0) throw new ArgumentOutOfRangeException(nameof(text)); return value; }
            bool format = false;
            try { ParseCount("oops"); } catch (FormatException) { format = true; }
            Check(format && ParseCount("3") == 3, "format and success are distinct");
        }
        Console.WriteLine("csharp-023: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** Malformed numeric text is caught as a format error.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            Exception? observed = null;
            try { try { throw new IOException("synthetic read failure"); } catch (IOException cause) { throw new InvalidOperationException("import failed", cause); } }
            catch (InvalidOperationException error) { observed = error; }
            Check(observed?.InnerException is IOException, "cause retained");
        }
        Console.WriteLine("csharp-023: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The outer domain failure still contains the I/O cause.

## Exercises

1. **Predict and explain.** Identify which failure category each catch handles.

2. **Guided modification.** Add a separate negative-count case without classifying it as FormatException.

3. **Independent construction.** Define an import API with distinct invalid-input and storage-failure outcomes.

4. **Diagnose a defect.** Diagnose catch-all code that returns an empty successful report.

5. **Boundary evidence.** Test success, expected rejection and an unexpected exception separately.

6. **Transfer and justify.** Decide which layer owns user-facing error translation and which details should remain private diagnostics.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Exception, Stack trace, Translation without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
