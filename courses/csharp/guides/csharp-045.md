# csharp-045: Reflection, native boundaries and AOT tradeoffs

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-044`

## Learning objectives

Replace string-based access in a small report with a typed projection. Then plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.

## Purpose and mental model

Reflection inspects types and members at runtime. It is useful for tooling and frameworks, but unrestricted dynamic discovery makes deployment analysis harder. Trimming removes code that appears unused, and ahead-of-time compilation moves work from startup to build. Reflection-heavy paths may need annotations, generated metadata or a different design.

Calling native code adds an ABI boundary: layout, calling convention, string encoding, allocation ownership and error reporting must agree. This route deliberately avoids unsafe native calls in its ordinary pad. The portable examples compare reflection with explicit typed access; an external Native AOT publish remains a separate platform-specific build exercise.

## Vocabulary and concepts

**Reflection:** Runtime inspection of program metadata.

**AOT:** Ahead-of-time compilation before application execution.

**ABI:** The binary-level agreement between compiled components.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`typeof(T)` gets type metadata; GetProperty returns a possibly absent member. Typed access is checked at compile time. Native AOT uses a publish property and platform toolchain requirements rather than a magic source keyword.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Inspect declared metadata

Runtime lookup needs an absence policy even when the programmer expects a member to exist.

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
      var property = typeof(Metric).GetProperty(nameof(Metric.Count));
      Check(property is not null && property.PropertyType == typeof(int),
            "known metadata");
      Check(typeof(Metric).GetProperty("Missing") is null, "absent member");
    }
    Console.WriteLine("csharp-045: passed");
    await Task.CompletedTask;
  }

  public record Metric(int Count);
}
```

**Observe:** The known property is an int and the missing property is absent.

### Example B: Prefer typed access for a fixed contract

A statically known relationship gives the compiler and deployment tools more information.

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
      var metric = new Metric(4);
      Func<Metric, int> getCount = value => value.Count;
      Check(getCount(metric) == 4, "typed projection");
    }
    Console.WriteLine("csharp-045: passed");
    await Task.CompletedTask;
  }

  public record Metric(int Count);
}
```

**Observe:** The fixed projection needs no string-based member lookup.

## Exercises

1. **Predict and explain.** Compare compile-time and runtime checking in the two examples.

2. **Guided modification.** Inspect a different known property and handle absence explicitly.

3. **Independent construction.** Replace string-based access in a small report with a typed projection.

4. **Diagnose a defect.** Diagnose assuming dynamic reflection will remain available after trimming.

5. **Boundary evidence.** Test an absent member and an unexpected member type.

6. **Transfer and justify.** Plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Reflection, AOT, ABI without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-045: Reflection, native boundaries and AOT tradeoffs.
Read courses/csharp/guides/csharp-045.md and courses/csharp/lessons/csharp-045.cs. Prerequisites: csharp-044.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-045_solution.cs and
courses/csharp/solutions/csharp-045_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
