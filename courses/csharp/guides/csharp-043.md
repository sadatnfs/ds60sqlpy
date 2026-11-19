# csharp-043: Projects, packages and reproducible builds

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-042`

## Learning objectives

Explain restore, build, run and publish, and check the target framework a build actually produced. The central exercise is task 3: Move a pure domain type into the supplied class-library project and run its executable checks.

## Purpose and mental model

A project file records the compilation target and build policy. Source that compiles against one framework can fail against another if it uses unavailable APIs. Pin a supported SDK policy and target framework deliberately. Package references add another versioned dependency surface, including transitive dependencies and restore behavior.

The classroom builds a fixed net10.0 project without arbitrary packages. External multi-file labs teach the project workflow explicitly: restore during preparation, build without changing dependencies, run tests, then publish a selected artifact. A portable build does not prove every architecture or operating system works. Keep actual build and runtime evidence separate.

## Vocabulary and concepts

**Target framework:** The API/runtime contract selected by a project.

**Restore:** Resolving dependency assets before build.

**Publish:** Producing a deployment-oriented application output.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Use [DomainLab](../fixtures/DomainLab/README.md) for the complete multi-project workflow. It has no third-party package dependencies.

## Syntax anatomy and execution trace

`TargetFramework` selects net10.0. Nullable and ImplicitUsings are compile policies. `dotnet restore`, `dotnet build --no-restore`, `dotnet run --no-build` and `dotnet publish` have distinct responsibilities.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Expose environment facts without overclaiming

Runtime facts are useful diagnostics but do not replace a source and project review.

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
      Check(Environment.Version.Major >= 10, "declared runtime generation");
      Check(typeof(List<int>).Assembly.GetName().Name is not null,
            "framework assembly identity");
    }
    Console.WriteLine("csharp-043: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The running framework generation is compatible with the declared classroom target.

### Example B: Read the compiled target framework

Both values come from the build and the runtime rather than from a hand-written table, so the checks fail if the project targets another framework. A real multi-project fixture is still required to qualify restore and publish behavior.

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
      string? target = AppContext.TargetFrameworkName;
      Check(target == ".NETCoreApp,Version=v10.0", "compiled target framework");
      Check(Environment.Version.Major == 10, "running runtime generation");
    }
    Console.WriteLine("csharp-043: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The compiled program reports .NETCoreApp,Version=v10.0, the framework its project targeted, and runs on a .NET 10 runtime.

## Exercises

1. **Predict and explain.** Explain the distinct purpose of restore, build, run and publish.

2. **Guided modification.** Build the checked-in DomainLab without adding a package.

3. **Independent construction.** Move a pure domain type into the supplied class-library project and run its executable checks.

4. **Diagnose a defect.** Diagnose an API unavailable under a different target framework.

5. **Boundary evidence.** Delete only the lab-owned output directories and verify a clean rebuild.

6. **Transfer and justify.** Design a dependency update review including lock changes, license checks and runtime evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. The separate explanation gives an executed reference answer where one has been written and says plainly where none exists yet. Open it only after your own attempt, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Reproduce Example A (Expose environment facts without overclaiming) before changing anything, and confirm its observation: The running framework generation is compatible with the declared classroom target.
2. Compare Example B (Read the compiled target framework) with Example A and name the first line whose behavior differs. Its observation is: The compiled program reports .NETCoreApp,Version=v10.0, the framework its project targeted, and runs on a .NET 10 runtime.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An SDK version and target framework are related but different.

## Self-check and next step

Explain Target framework, Restore, Publish without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-043: Projects, packages and reproducible builds.
Read courses/csharp/guides/csharp-043.md and courses/csharp/lessons/csharp-043.cs. Prerequisites: csharp-042.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-043_solution.cs and
courses/csharp/solutions/csharp-043_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
