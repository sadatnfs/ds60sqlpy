# csharp-043: Projects, packages and reproducible builds

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-042`

## Learning objectives

Move a pure domain type into the supplied class-library project and run its executable checks. Then design a dependency update review including lock changes, license checks and runtime evidence.

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

### Example B: Keep configuration explicit

A real project fixture, rather than this metadata demonstration, is required to qualify multi-file build behavior.

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
      var configuration =
          new Dictionary<string, string> { ["target"] = "net10.0",
                                           ["nullable"] = "enable" };
      Check(configuration["target"] == "net10.0" &&
                configuration["nullable"] == "enable",
            "reviewed build contract");
    }
    Console.WriteLine("csharp-043: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The example preserves the intended target and nullable policy.

## Exercises

1. **Predict and explain.** Explain the distinct purpose of restore, build, run and publish.

2. **Guided modification.** Build the checked-in DomainLab without adding a package.

3. **Independent construction.** Move a pure domain type into the supplied class-library project and run its executable checks.

4. **Diagnose a defect.** Diagnose an API unavailable under a different target framework.

5. **Boundary evidence.** Delete only the lab-owned output directories and verify a clean rebuild.

6. **Transfer and justify.** Design a dependency update review including lock changes, license checks and runtime evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Target framework, Restore, Publish without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
