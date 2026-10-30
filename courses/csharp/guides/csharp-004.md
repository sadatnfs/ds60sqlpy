# csharp-004: Strings, interpolation and Unicode text

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-003`

## Learning objectives

Implement case-insensitive machine-key comparison with an explicit policy. Then design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.

## Purpose and mental model

A string is an immutable sequence of UTF-16 code units. Immutability means an operation such as replacement returns a new string; it does not edit the original object. Human-visible characters are more complicated than code units: some Unicode scalar values need two units, and a visible grapheme can combine several scalar values. Choose the unit that matches the task before counting or slicing text.

Text comparison also has a policy. Machine identifiers usually need ordinal comparison; user-facing sorting can need culture rules. Encoding turns text into bytes for a file or protocol. UTF-8 byte length is not string Length, and neither is automatically the number of visible characters. Keep these boundaries distinct when limiting input.

## Vocabulary and concepts

**Code unit:** One storage unit of an encoding, here a UTF-16 char.

**Unicode scalar:** A code point excluding surrogate values.

**Encoding:** A mapping between text and bytes.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`$"item {count}"` interpolates a value. `StringComparison.OrdinalIgnoreCase` makes a comparison policy explicit. `EnumerateRunes()` visits Unicode scalar values. `Encoding.UTF8.GetByteCount` measures an encoded representation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Immutable transformations

Assignment of the returned value is necessary to keep a transformation. An explicit comparison policy prevents dependence on ambient culture.

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
      string original = "data";
      string changed = original.ToUpperInvariant();
      Check(original == "data" && changed == "DATA", "strings are unchanged");
      Check(string.Equals("KEY", "key", StringComparison.OrdinalIgnoreCase),
            "identifier comparison");
    }
    Console.WriteLine("csharp-004: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The original remains data while the result is DATA.

### Example B: Choose the counting unit

The fixture disproves the assumption that Length is a universal character count.

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
      string symbol = "😀";
      Check(symbol.Length == 2, "UTF-16 units");
      Check(symbol.EnumerateRunes().Count() == 1, "Unicode scalar");
      Check(Encoding.UTF8.GetByteCount(symbol) == 4, "UTF-8 bytes");
    }
    Console.WriteLine("csharp-004: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** One scalar occupies two UTF-16 units and four UTF-8 bytes.

## Exercises

1. **Predict and explain.** Predict both string values after ToUpperInvariant and explain ownership of the result.

2. **Guided modification.** Build an interpolated label containing a count and a unit.

3. **Independent construction.** Implement case-insensitive machine-key comparison with an explicit policy.

4. **Diagnose a defect.** Diagnose code that takes one char from the emoji and assumes it is a complete symbol.

5. **Boundary evidence.** Compare ASCII, an emoji and a combining-mark sequence using code units and text elements.

6. **Transfer and justify.** Design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Code unit, Unicode scalar, Encoding without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-004: Strings, interpolation and Unicode text.
Read courses/csharp/guides/csharp-004.md and courses/csharp/lessons/csharp-004.cs. Prerequisites: csharp-003.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-004_solution.cs and
courses/csharp/solutions/csharp-004_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
