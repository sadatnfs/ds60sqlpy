# csharp-045: Reflection, native boundaries and AOT tradeoffs

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-044`

## Learning objectives

Weigh reflection against typed access and explain what trimming and AOT require. The central exercise is task 3: Replace string-based access in a small report with a typed projection.

## Purpose and mental model

Reflection inspects types and members at runtime. It is useful for tooling and frameworks, but unrestricted dynamic discovery makes deployment analysis harder. Trimming removes code that appears unused, and ahead-of-time compilation moves work from startup to build. Reflection-heavy paths may need annotations, generated metadata or a different design.

Calling native code adds an ABI boundary: layout, calling convention, string encoding, allocation ownership and error reporting must agree. This route deliberately avoids unsafe native calls in its ordinary pad. The portable examples compare reflection with explicit typed access; an external Native AOT publish remains a separate platform-specific build exercise.

## Vocabulary and concepts

**Reflection:** Runtime inspection of program metadata.

**AOT:** Ahead-of-time compilation before application execution.

**ABI:** The binary-level agreement between compiled components.

## How to run this lesson

The reflection calls hang off `System.Type`, so `typeof(Metric).GetProperty` needs no extra import. Native AOT is not used here: it is enabled with the `PublishAot` project property and a `dotnet publish` for a specific runtime identifier, and it needs a platform linker that the classroom pad does not provide.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`typeof(T)` gets type metadata; GetProperty returns a possibly absent member. Typed access is checked at compile time. Native AOT uses a publish property and platform toolchain requirements rather than a magic source keyword.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `nameof(Metric.Count)` becomes the string Count at compile time, so a rename updates it. `GetProperty` searches the record's public instance properties for that name and returns a `PropertyInfo` whose `PropertyType` is `int`. Searching for Missing returns null rather than throwing, and so does a lowercase count, because the default lookup is case-sensitive.

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

**Trace.** `Metric(4)` stores 4 in `Count`. The lambda `value => value.Count` is compiled against the property directly, so the compiler verifies the member exists and returns an `int`. Calling it returns 4. No name string is looked up at run time, which also tells trimming and AOT tools exactly which member the program uses.

## Exercises

1. **Predict and explain.** Compare compile-time and runtime checking in the two examples.

2. **Guided modification.** Inspect a different known property and handle absence explicitly.

3. **Independent construction.** Replace string-based access in a small report with a typed projection.

4. **Diagnose a defect.** Diagnose assuming dynamic reflection will remain available after trimming.

5. **Boundary evidence.** Test an absent member and an unexpected member type.

6. **Transfer and justify.** Plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.

For task 4, code that finds members by strings read at run time can lose them when the trimmer removes unused metadata, and trim analysis warns during publish about calls it cannot analyze. For task 5, handle a null `PropertyInfo` explicitly, and compare `PropertyType` with the expected type before reading the value.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Inspect declared metadata) before changing anything, and confirm its observation: The known property is an int and the missing property is absent.
2. Compare Example B (Prefer typed access for a fixed contract) with Example A and name the first line whose behavior differs. Its observation is: The fixed projection needs no string-based member lookup.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Publishing AOT does not guarantee a smaller or faster application for every workload.

## Self-check and next step

Mark which check in each example the compiler performs and which the runtime performs. Explain why `GetProperty` returning null is a normal outcome. For task 6, write the experiment plan: runtime identifier, the `PublishAot` property, the native toolchain needed, and the checks that compare the AOT binary with the managed build.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/): The Native AOT deployment overview explains the publish property, platform prerequisites and the limits on reflection and dynamic code.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
