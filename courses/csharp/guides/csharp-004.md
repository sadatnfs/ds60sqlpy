# csharp-004: Strings, interpolation and Unicode text

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-003`

## Learning objectives

Compare, transform and measure strings with explicit culture and Unicode policies. The central exercise is task 3: Implement case-insensitive machine-key comparison with an explicit policy.

## Purpose and mental model

A string is an immutable sequence of UTF-16 code units. Immutability means an operation such as replacement returns a new string; it does not edit the original object. Human-visible characters are more complicated than code units: some Unicode scalar values need two units, and a visible grapheme can combine several scalar values. Choose the unit that matches the task before counting or slicing text.

Text comparison also has a policy. Machine identifiers usually need ordinal comparison; user-facing sorting can need culture rules. Encoding turns text into bytes for a file or protocol. UTF-8 byte length is not string Length, and neither is automatically the number of visible characters. Keep these boundaries distinct when limiting input.

## Vocabulary and concepts

**Code unit:** One storage unit of an encoding, here a UTF-16 char.

**Unicode scalar:** A code point excluding surrogate values.

**Encoding:** A mapping between text and bytes.

## How to run this lesson

`EnumerateRunes` and `Encoding` live in `System.Text`, which the worked programs import explicitly because the project's implicit usings omit it. A terminal without a suitable font may draw a box for the emoji, but the checks count units in memory, so they pass whatever the display shows.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`$"item {count}"` interpolates a value. `StringComparison.OrdinalIgnoreCase` makes a comparison policy explicit. `EnumerateRunes()` visits Unicode scalar values. `Encoding.UTF8.GetByteCount` measures an encoded representation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `original` refers to the string data. `ToUpperInvariant()` cannot change that string, because .NET strings are immutable; it builds a new string, DATA, and returns it, and the assignment stores that reference in `changed`. The first check confirms both values. `string.Equals` with `OrdinalIgnoreCase` compares KEY and key using a fixed, culture-free case mapping, so the result does not depend on the machine's language setting.

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

**Trace.** The emoji lies outside the 16-bit range, so UTF-16 stores it as a surrogate pair and `symbol.Length` counts two `char` values. `EnumerateRunes()` decodes that pair back into one Unicode scalar, so its count is 1. `Encoding.UTF8.GetByteCount` measures the same scalar after encoding to UTF-8, which takes four bytes. Three questions about one symbol give three answers: 2, 1 and 4.

## Exercises

1. **Predict and explain.** Predict both string values after ToUpperInvariant and explain ownership of the result.

2. **Guided modification.** Build an interpolated label containing a count and a unit.

3. **Independent construction.** Implement case-insensitive machine-key comparison with an explicit policy.

4. **Diagnose a defect.** Diagnose code that takes one char from the emoji and assumes it is a complete symbol.

5. **Boundary evidence.** Compare ASCII, an emoji and a combining-mark sequence using code units and text elements.

6. **Transfer and justify.** Design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.

For task 4, `symbol[0]` is the high surrogate U+D83D, which `char.IsHighSurrogate` confirms: half of a symbol, not a complete one. For task 5, `"e\u0301"`, an e followed by a combining acute accent, has Length 2 and two runes, yet `StringInfo` counts one text element, so even runes overcount what a reader sees.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Immutable transformations) before changing anything, and confirm its observation: The original remains data while the result is DATA.
2. Compare Example B (Choose the counting unit) with Example A and name the first line whose behavior differs. Its observation is: One scalar occupies two UTF-16 units and four UTF-8 bytes.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Indexing a string can split a surrogate pair.

## Self-check and next step

Give the Length, rune count and UTF-8 byte count of the text a, precomposed é, then the emoji. Explain why the result of `ToUpperInvariant` must be assigned to be kept. Say which comparison policy suits a machine key and which suits text shown to a user, and explain why they differ.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): From the C# documentation, the .NET fundamentals article on character encoding explains UTF-16 code units, surrogate pairs, `Rune` and grapheme clusters.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
