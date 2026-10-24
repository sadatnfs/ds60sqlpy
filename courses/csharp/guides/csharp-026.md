# csharp-026: JSON contracts and schema evolution

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-025`

## Learning objectives

Write a decoder returning explicit validation errors for missing name and negative quantity. Then design a migration from a renamed quantity field while retaining old saved records.

## Purpose and mental model

JSON provides a portable syntax for values, arrays and objects; it does not define the business schema. Deserializing into a type supplies a structural mapping, but required domain rules still need validation. A missing property can become a default value, and a syntactically valid object can still be meaningless for the application.

Schema evolution requires deciding what happens when fields are added, removed or renamed. A version field and explicit migration can preserve meaning. Do not equate a successful deserialize call with a safe external object. Validate ranges and identities before admitting the object into domain logic, and avoid serializing internal secrets merely because a public property exists.

## Vocabulary and concepts

**Serialization:** Encoding an object representation into data.

**Schema:** The expected structure and meaning of fields.

**Migration:** A deliberate conversion between schema versions.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`JsonSerializer.Serialize` creates JSON text. `Deserialize<T>` maps it into T and can return null. Records provide compact transport shapes. Serialization options control naming and formatting but do not replace domain validation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Round-trip a small transport record

Equality checks the modeled data rather than incidental property ordering in JSON text.

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
            var original = new ItemDto("pear", 3);
            string json = JsonSerializer.Serialize(original);
            var restored = JsonSerializer.Deserialize<ItemDto>(json);
            Check(restored == original, "record round trip");
        }
        Console.WriteLine("csharp-026: passed");
        await Task.CompletedTask;
    }

    public record ItemDto(string Name, int Quantity);
    public static bool Valid(ItemDto item) => !string.IsNullOrWhiteSpace(item.Name) && item.Quantity >= 0;
}
```

**Observe:** The restored name and quantity match the original record.

### Example B: Validate after structural decoding

Parsing answers whether the representation is understood. Validation answers whether the application may use it.

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
            var invalid = JsonSerializer.Deserialize<ItemDto>("{\"Name\":\"pear\",\"Quantity\":-2}");
            Check(invalid is not null && !Valid(invalid), "domain rejection after decoding");
            Check(!Valid(new ItemDto("", 2)), "empty identity rejected");
        }
        Console.WriteLine("csharp-026: passed");
        await Task.CompletedTask;
    }

    public record ItemDto(string Name, int Quantity);
    public static bool Valid(ItemDto item) => !string.IsNullOrWhiteSpace(item.Name) && item.Quantity >= 0;
}
```

**Observe:** Valid JSON can decode into a rejected domain value.

## Exercises

1. **Predict and explain.** Predict what round-trip equality establishes and what it does not.

2. **Guided modification.** Add a clearly versioned optional description field.

3. **Independent construction.** Write a decoder returning explicit validation errors for missing name and negative quantity.

4. **Diagnose a defect.** Diagnose trusting default values from missing JSON fields.

5. **Boundary evidence.** Test malformed JSON, JSON null and an extra unknown field.

6. **Transfer and justify.** Design a migration from a renamed quantity field while retaining old saved records.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

JSON text equality is sensitive to formatting and property ordering. Structural decoding does not enforce every domain invariant. Keep public transport models separate from internal objects carrying credentials or resources.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Serialization, Schema, Migration without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-026: JSON contracts and schema evolution.
Read courses/csharp/guides/csharp-026.md and courses/csharp/lessons/csharp-026.cs. Prerequisites: csharp-025.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-026_solution.cs and
courses/csharp/solutions/csharp-026_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
