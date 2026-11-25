# csharp-016: Foundation project: a validated inventory report

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-015`

## Learning objectives

Build a validated inventory importer that reports accepted totals and rejected lines deterministically. The central exercise is task 3: Build a sorted text report from the accepted dictionary and the rejection count.

## Purpose and mental model

A useful first project combines parsing, representation and aggregation while keeping their responsibilities separate. The input boundary rejects malformed quantities. The domain representation preserves item identity. The report stage summarizes only accepted records. Mixing these stages often creates a subtle bug: a failed parse becomes zero and then appears as valid data.

This project uses in-memory fixture lines so it runs offline without interactive input. It reports accepted totals and rejected line counts independently. A real importer would also record line identity and a safe reason. Build the smallest end-to-end path first, then introduce invalid and duplicate inputs. The final result must explain what happened, not merely produce a total that looks plausible.

## Vocabulary and concepts

**Pipeline:** Stages that transform validated information.

**Rejection:** An input excluded under an explicit rule.

**Aggregation:** Combining accepted records into a summary.

## How to run this lesson

The project's `Import` helper is a single long line after `Main`; reformat a copy in your pad if you want to trace it. It returns a tuple, so `totals.Counts` and `totals.Rejected` are tuple element names, not properties of a class. The dictionary uses `StringComparer.Ordinal`, so Pear and pear count separately.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Split` produces fields; check the field count before indexing. `TryParse` separates syntax from a valid integer. `TryGetValue` supports accumulating repeated keys. Sorting keys before display gives a stable report.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var totals = Import(new[] { "pear,2", "apple,3", "pear,4" });
      Check(totals.Rejected == 0, "all accepted");
      Check(totals.Counts["pear"] == 6 && totals.Counts["apple"] == 3,
            "per-item totals");
    }
    Console.WriteLine("csharp-016: passed");
    await Task.CompletedTask;
  }

  public static (Dictionary<string, int> Counts, int Rejected)
      Import(IEnumerable<string> lines) {
    var counts = new Dictionary<string, int>(StringComparer.Ordinal);
    int rejected = 0;
    foreach (string line in lines) {
      string[] fields = line.Split(',');
      if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) ||
          !int.TryParse(fields[1], out int quantity) || quantity < 0) {
        rejected++;
        continue;
      }
      counts.TryGetValue(fields[0], out int before);
      counts[fields[0]] = checked(before + quantity);
    }
    return (counts, rejected);
  }
}
```

**Observe:** Pear totals 6 and apple totals 3.

**Trace.** For pear,2, `Split` gives two fields, the name is not blank, `TryParse` yields 2 and the quantity is not negative. `TryGetValue` finds no pear, writes 0 into `before`, and the indexer stores 2. Apple,3 stores 3. Pear,4 finds the earlier 2 and stores the checked sum 6. Nothing was rejected.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var totals = Import(new[] { "pear,2", "pear,no", "apple,-1", "broken" });
      Check(totals.Rejected == 3, "rejections counted");
      Check(totals.Counts.Count == 1 && totals.Counts["pear"] == 2,
            "only valid data contributes");
      Check(Import(Array.Empty<string>()).Counts.Count == 0, "empty input");
    }
    Console.WriteLine("csharp-016: passed");
    await Task.CompletedTask;
  }

  public static (Dictionary<string, int> Counts, int Rejected)
      Import(IEnumerable<string> lines) {
    var counts = new Dictionary<string, int>(StringComparer.Ordinal);
    int rejected = 0;
    foreach (string line in lines) {
      string[] fields = line.Split(',');
      if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) ||
          !int.TryParse(fields[1], out int quantity) || quantity < 0) {
        rejected++;
        continue;
      }
      counts.TryGetValue(fields[0], out int before);
      counts[fields[0]] = checked(before + quantity);
    }
    return (counts, rejected);
  }
}
```

**Observe:** Three rejected lines do not alter the valid pear total.

**Trace.** Pear,2 is accepted. Pear,no splits into two fields but fails `TryParse`, so `rejected` becomes 1. Apple,-1 parses, then fails `quantity < 0`, giving 2. Broken has one field and is rejected before any indexing, giving 3. Only pear survives with 2, and an empty array returns an empty dictionary with zero rejections.

## Exercises

1. **Predict and explain.** Trace each input through validation and accumulation.

2. **Guided modification.** Add one valid duplicate and predict the new total before running.

3. **Independent construction.** Build a sorted text report from the accepted dictionary and the rejection count.

4. **Diagnose a defect.** Diagnose an importer that ignores TryParse failure and inserts zero.

5. **Boundary evidence.** Test empty item names, extra fields, zero quantity and empty input.

6. **Transfer and justify.** Design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.

For task 4, an importer that ignores the `TryParse` result stores 0 for pear,no, so a corrupt line becomes a legitimate looking item with zero stock. For task 5, include a blank name such as a line starting with a comma, a line with three fields and pear,0; `int.TryParse` also accepts a space before the 2 in pear, 2.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Aggregate repeated valid items) before changing anything, and confirm its observation: Pear totals 6 and apple totals 3.
2. Compare Example B (Retain rejection evidence) with Example A and name the first line whose behavior differs. Its observation is: Three rejected lines do not alter the valid pear total.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Checking field count after indexing is too late.

## Self-check and next step

Trace the dictionary after each line of pear,2 then Pear,3 then pear,1 under the ordinal comparer. Explain why the field count is checked before `fields[1]` is read. For task 6, describe what a per-line rejection record stores and which raw text it should leave out.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `String.Split` and `Int32.TryParse` API pages, together with the dictionary reference, cover the parsing and accumulation steps used here.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
