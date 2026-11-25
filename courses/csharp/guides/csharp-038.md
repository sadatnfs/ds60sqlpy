# csharp-038: Validation, regular expressions and bounded input

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-037`

## Learning objectives

Validate bounded input with non-backtracking regular expressions and separate domain rules. The central exercise is task 3: Validate a structured identifier and then check its domain-specific reserved words.

## Purpose and mental model

Validation defines what an input means and which representations are accepted. A regular expression can recognize a textual shape, but it does not enforce every semantic rule. A date-shaped string can still name an impossible date. Keep size, syntax and domain validation as separate steps.

Backtracking expressions can require excessive work on adversarial inputs. Use a bounded input length, a timeout and an appropriate engine mode. Prefer simple parsers when they make the contract clearer. Never construct a regex from untrusted text without deciding whether that text is literal or syntax.

## Vocabulary and concepts

**Syntax validation:** Checking representational structure.

**Semantic validation:** Checking whether represented values make sense.

**ReDoS:** Resource exhaustion caused by costly regular-expression behavior.

## How to run this lesson

The regex type comes from `System.Text.RegularExpressions`, imported for the worked examples. Both patterns use `RegexOptions.NonBacktracking`, a linear-time engine that rejects some constructs: a backreference such as `(a)\1` throws `NotSupportedException` when the regex is constructed, so that failure appears before any input is matched.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`RegexOptions.NonBacktracking` supports a bounded engine for compatible patterns. Anchors constrain the entire input. Regex.Escape treats input as literal pattern text. Domain validation follows a successful shape match.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var pattern =
          new Regex(@"\A[a-z][a-z0-9_]{0,15}\z", RegexOptions.NonBacktracking,
                    TimeSpan.FromSeconds(1));
      Check(pattern.IsMatch("report_2"), "accepted identifier");
      Check(!pattern.IsMatch("2report") && !pattern.IsMatch("report!"),
            "rejected shapes");
    }
    Console.WriteLine("csharp-038: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The identifier begins with a lowercase letter and uses only admitted characters.

**Trace.** The pattern starts with `\A`, so matching must begin at the first character, and ends with `\z`, so it must finish at the last. report_2 starts with a lowercase letter and continues with seven admitted characters, so it matches. 2report fails the first character class, and report! fails because the exclamation mark is outside the class and `\z` forbids stopping early.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      string literal = "a+b";
      var pattern =
          new Regex(@"\A" + Regex.Escape(literal) + @"\z",
                    RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));
      Check(pattern.IsMatch("a+b") && !pattern.IsMatch("aaab"),
            "escaped literal");
    }
    Console.WriteLine("csharp-038: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The plus sign is matched literally.

**Trace.** `Regex.Escape("a+b")` returns `a\+b`, so the plus sign becomes a literal character instead of a one-or-more operator. Wrapped in the anchors, the pattern accepts only the exact three-character text a+b. The input aaab fails, although the unescaped pattern a+b would match it, because a+ consumes the repeated letters before b and then finds the final b.

## Exercises

1. **Predict and explain.** Explain every part of the identifier pattern.

2. **Guided modification.** Change the maximum identifier length and test the exact boundary.

3. **Independent construction.** Validate a structured identifier and then check its domain-specific reserved words.

4. **Diagnose a defect.** Diagnose matching a valid substring inside an invalid full input.

5. **Boundary evidence.** Test newline, empty input and one character beyond the limit.

6. **Transfer and justify.** Choose a parser or regex for a nested format and justify complexity and error reporting.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.

Task 4 reproduces itself if you drop the anchors: the unanchored class pattern finds a valid run inside 2report and inside report!, so both invalid inputs report a match. For task 5, the `\z` anchor rejects report followed by a newline, while a `$` anchor accepts it, because `$` may match just before a final newline. Empty input and a seventeen-character identifier both fail.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Validate a bounded identifier) before changing anything, and confirm its observation: The identifier begins with a lowercase letter and uses only admitted characters.
2. Compare Example B (Keep literal user text literal) with Example A and name the first line whose behavior differs. Its observation is: The plus sign is matched literally.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A timeout is a fallback, not a substitute for a simple pattern and bounded input.

## Self-check and next step

Name the shortest and longest identifiers the pattern accepts and give their lengths. Explain why escaping user text keeps its meaning as data. For task 6, compare a regex with a small hand-written parser for a nested format, judging which one can report where the input went wrong and which one bounds its running time.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET regular expression articles cover anchors, `Regex.Escape`, match timeouts and the nonbacktracking option.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
