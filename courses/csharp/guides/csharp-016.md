# csharp-016: Foundation project: a validated inventory report

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-015`

## Learning objectives

Build a sorted text report from the accepted dictionary and the rejection count. Then design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.

## Purpose and mental model

A useful first project combines parsing, representation and aggregation while keeping their responsibilities separate. The input boundary rejects malformed quantities. The domain representation preserves item identity. The report stage summarizes only accepted records. Mixing these stages often creates a subtle bug: a failed parse becomes zero and then appears as valid data.

This project uses in-memory fixture lines so it runs offline without interactive input. It reports accepted totals and rejected line counts independently. A real importer would also record line identity and a safe reason. Build the smallest end-to-end path first, then introduce invalid and duplicate inputs. The final result must explain what happened, not merely produce a total that looks plausible.

## Vocabulary and concepts

**Pipeline:** Stages that transform validated information.

**Rejection:** An input excluded under an explicit rule.

**Aggregation:** Combining accepted records into a summary.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Split` produces fields; check the field count before indexing. `TryParse` separates syntax from a valid integer. `TryGetValue` supports accumulating repeated keys. Sorting keys before display gives a stable report.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Aggregate repeated valid items

Repeated identities accumulate after validation rather than creating ambiguous duplicate dictionary entries.

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
            var totals = Import(new[] { "pear,2", "apple,3", "pear,4" });
            Check(totals.Rejected == 0, "all accepted");
            Check(totals.Counts["pear"] == 6 && totals.Counts["apple"] == 3, "per-item totals");
        }
        Console.WriteLine("csharp-016: passed");
        await Task.CompletedTask;
    }

    public static (Dictionary<string, int> Counts, int Rejected) Import(IEnumerable<string> lines) { var counts = new Dictionary<string, int>(StringComparer.Ordinal); int rejected = 0; foreach (string line in lines) { string[] fields = line.Split(','); if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) || !int.TryParse(fields[1], out int quantity) || quantity < 0) { rejected++; continue; } counts.TryGetValue(fields[0], out int before); counts[fields[0]] = checked(before + quantity); } return (counts, rejected); }
}
```

**Observe:** Pear totals 6 and apple totals 3.

### Example B: Retain rejection evidence

Malformed and negative quantities remain excluded, and empty input produces an empty report rather than an invented item.

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
            var totals = Import(new[] { "pear,2", "pear,no", "apple,-1", "broken" });
            Check(totals.Rejected == 3, "rejections counted");
            Check(totals.Counts.Count == 1 && totals.Counts["pear"] == 2, "only valid data contributes");
            Check(Import(Array.Empty<string>()).Counts.Count == 0, "empty input");
        }
        Console.WriteLine("csharp-016: passed");
        await Task.CompletedTask;
    }

    public static (Dictionary<string, int> Counts, int Rejected) Import(IEnumerable<string> lines) { var counts = new Dictionary<string, int>(StringComparer.Ordinal); int rejected = 0; foreach (string line in lines) { string[] fields = line.Split(','); if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) || !int.TryParse(fields[1], out int quantity) || quantity < 0) { rejected++; continue; } counts.TryGetValue(fields[0], out int before); counts[fields[0]] = checked(before + quantity); } return (counts, rejected); }
}
```

**Observe:** Three rejected lines do not alter the valid pear total.

## Exercises

1. **Predict and explain.** Trace each input through validation and accumulation.

2. **Guided modification.** Add one valid duplicate and predict the new total before running.

3. **Independent construction.** Build a sorted text report from the accepted dictionary and the rejection count.

4. **Diagnose a defect.** Diagnose an importer that ignores TryParse failure and inserts zero.

5. **Boundary evidence.** Test empty item names, extra fields, zero quantity and empty input.

6. **Transfer and justify.** Design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Pipeline, Rejection, Aggregation without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-016: Foundation project: a validated inventory report.
Read courses/csharp/guides/csharp-016.md and courses/csharp/lessons/csharp-016.cs. Prerequisites: csharp-015.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-016_solution.cs and
courses/csharp/solutions/csharp-016_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
