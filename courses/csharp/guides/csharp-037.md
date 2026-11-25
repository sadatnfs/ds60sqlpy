# csharp-037: Algorithmic complexity and measured performance

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-036`

## Learning objectives

Compare an algorithm's work with and without an index while keeping the same equality policy. The central exercise is task 3: Compare repeated list scans with one built index while preserving equality policy.

## Purpose and mental model

Performance begins with an explicit workload and cost model. A nested search can perform quadratically many comparisons, while an indexed lookup may trade memory for near-constant expected lookup cost. Big-O describes growth, not an exact elapsed time or a universal ranking. Constant factors, data layout and input size matter.

Measure correctness separately from speed. A benchmark that computes a different result is irrelevant. Warmup, allocation, runtime optimization and background load can distort tiny timings. The classroom counts deterministic operations to explain growth; a prepared external benchmark project is the right place for statistically meaningful elapsed-time comparisons.

## Vocabulary and concepts

**Complexity:** How a resource requirement grows with input size.

**Cost model:** The operations or resources being counted.

**Benchmark:** A controlled measurement of implementation behavior.

## How to run this lesson

Both examples are deterministic: they count comparisons and stored entries instead of timing anything, so the result is the same on a slow laptop and a fast server. The lesson needs no extra imports, since `HashSet<int>` lives in `System.Collections.Generic`, which the worked examples already include. Read the counts as a model of work, not a measurement of seconds.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

HashSet membership can avoid repeated linear scans. Distinct and grouping have equality-policy assumptions. Count comparisons in a fixture instead of asserting a fragile timing threshold.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Count a linear search

The deterministic count illustrates the algorithm independently of machine speed.

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
      int[] values = { 2, 4, 6, 8 };
      int comparisons = 0;
      bool found = false;
      foreach (int value in values) {
        comparisons++;
        if (value == 8) {
          found = true;
          break;
        }
      }
      Check(found && comparisons == 4, "last-element linear search");
    }
    Console.WriteLine("csharp-037: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Finding the last element needs four comparisons.

**Trace.** `comparisons` starts at 0 and `found` at false. The loop visits 2, 4, 6 and 8 in order, adding one to the counter before each equality test. Only the fourth value equals 8, so the loop sets `found`, breaks, and leaves the counter at 4. Searching for 2 would stop after one comparison, while an absent 9 would visit all four values and finish with `found` still false.

### Example B: Trade memory for repeated membership

Building and retaining the index has a cost that should be amortized across enough queries.

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
      var index = new HashSet<int>(new[] { 2, 4, 6, 8 });
      Check(index.Contains(8) && !index.Contains(9), "indexed membership");
      Check(index.Count == 4, "index has stored identities");
    }
    Console.WriteLine("csharp-037: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The index answers membership while storing four identities.

**Trace.** The `HashSet<int>` constructor hashes 2, 4, 6 and 8 once and stores each in a bucket. `Contains(8)` hashes 8 and inspects the matching bucket instead of walking the whole sequence, and `Contains(9)` finds no match there. `Count` reports four stored identities. Building the set cost one full pass plus memory, which pays off only after enough later lookups.

## Exercises

1. **Predict and explain.** Count comparisons for first, last and absent targets.

2. **Guided modification.** Double the input size and predict worst-case linear comparisons.

3. **Independent construction.** Compare repeated list scans with one built index while preserving equality policy.

4. **Diagnose a defect.** Diagnose a benchmark that excludes index construction from a one-shot workload.

5. **Boundary evidence.** Test duplicate inputs and empty queries.

6. **Transfer and justify.** Write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.

In task 4, a benchmark that builds the index outside the timed region and then runs a single query reports the cheap lookup while hiding the construction pass that a one-shot workload must also pay. In task 5, duplicate inputs collapse: a set built from 2, 2 and 4 holds only two entries, and any query against an empty set returns false without error.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Count a linear search) before changing anything, and confirm its observation: Finding the last element needs four comparisons.
2. Compare Example B (Trade memory for repeated membership) with Example A and name the first line whose behavior differs. Its observation is: The index answers membership while storing four identities.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A single stopwatch sample is not reliable evidence.

## Self-check and next step

State the worst-case comparison count for a linear search over eight values, then over sixteen, and explain why it doubles. Describe when a single query makes building a `HashSet` a loss rather than a gain. For task 6, list the warmup, the correctness check run alongside each measurement, and the allocation figure you would report with the timing.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide and the `HashSet<T>` reference describe collection lookup behavior and the equality comparers that hashing relies on.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-037: Algorithmic complexity and measured performance.
Read courses/csharp/guides/csharp-037.md and courses/csharp/lessons/csharp-037.cs. Prerequisites: csharp-036.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-037_solution.cs and
courses/csharp/solutions/csharp-037_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
