# csharp-038: Validation, regular expressions and bounded input

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-037`

## Learning objectives

Validate a structured identifier and then check its domain-specific reserved words. Then choose a parser or regex for a nested format and justify complexity and error reporting.

## Purpose and mental model

Validation defines what an input means and which representations are accepted. A regular expression can recognize a textual shape, but it does not enforce every semantic rule. A date-shaped string can still name an impossible date. Keep size, syntax and domain validation as separate steps.

Backtracking expressions can require excessive work on adversarial inputs. Use a bounded input length, a timeout and an appropriate engine mode. Prefer simple parsers when they make the contract clearer. Never construct a regex from untrusted text without deciding whether that text is literal or syntax.

## Vocabulary and concepts

**Syntax validation:** Checking representational structure.

**Semantic validation:** Checking whether represented values make sense.

**ReDoS:** Resource exhaustion caused by costly regular-expression behavior.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`RegexOptions.NonBacktracking` supports a bounded engine for compatible patterns. Anchors constrain the entire input. Regex.Escape treats input as literal pattern text. Domain validation follows a successful shape match.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Validate a bounded identifier

Whole-input anchors prevent a valid substring from disguising an invalid full value.

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
            var pattern = new Regex(@"\A[a-z][a-z0-9_]{0,15}\z", RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));
            Check(pattern.IsMatch("report_2"), "accepted identifier");
            Check(!pattern.IsMatch("2report") && !pattern.IsMatch("report!"), "rejected shapes");
        }
        Console.WriteLine("csharp-038: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The identifier begins with a lowercase letter and uses only admitted characters.

### Example B: Keep literal user text literal

Escaping preserves data meaning instead of accidentally granting regex syntax authority.

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
            string literal = "a+b";
            var pattern = new Regex(@"\A" + Regex.Escape(literal) + @"\z", RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));
            Check(pattern.IsMatch("a+b") && !pattern.IsMatch("aaab"), "escaped literal");
        }
        Console.WriteLine("csharp-038: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The plus sign is matched literally.

## Exercises

1. **Predict and explain.** Explain every part of the identifier pattern.

2. **Guided modification.** Change the maximum identifier length and test the exact boundary.

3. **Independent construction.** Validate a structured identifier and then check its domain-specific reserved words.

4. **Diagnose a defect.** Diagnose matching a valid substring inside an invalid full input.

5. **Boundary evidence.** Test newline, empty input and one character beyond the limit.

6. **Transfer and justify.** Choose a parser or regex for a nested format and justify complexity and error reporting.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Syntax validation, Semantic validation, ReDoS without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-038: Validation, regular expressions and bounded input.
Read courses/csharp/guides/csharp-038.md and courses/csharp/lessons/csharp-038.cs. Prerequisites: csharp-037.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-038_solution.cs and
courses/csharp/solutions/csharp-038_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
