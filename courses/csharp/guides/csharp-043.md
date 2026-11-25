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

The pad checks only what a running program can report about itself. The project work happens in DomainLab, linked below, which needs a prepared .NET 10 SDK and runs `dotnet restore`, `dotnet build --no-restore` and `dotnet run --no-build` as separate steps. Nothing in the pad can prove that a restore or publish works.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Use [DomainLab](../fixtures/DomainLab/README.md) for the complete multi-project workflow. It has no third-party package dependencies.

## Syntax anatomy and execution trace

`TargetFramework` selects net10.0. Nullable and ImplicitUsings are compile policies. `dotnet restore`, `dotnet build --no-restore`, `dotnet run --no-build` and `dotnet publish` have distinct responsibilities.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `Environment.Version` reports the runtime executing the program; in the classroom worker it was 10.0.15, so `Major` is 10 and the first check passes. `typeof(List<int>).Assembly.GetName().Name` returns System.Private.CoreLib, the core library that holds `List<T>`. The check only asserts that a name exists, because the exact assembly layout is an implementation detail that can change.

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

**Trace.** `AppContext.TargetFrameworkName` comes from the compiled program, and the course project produced .NETCoreApp,Version=v10.0 because its project file says net10.0. `Environment.Version.Major` comes from the runtime, which is a separate fact: a later patch runtime keeps Major at 10. Changing the target in the project file would break the first check at run time.

## Exercises

1. **Predict and explain.** Explain the distinct purpose of restore, build, run and publish.

2. **Guided modification.** Build the checked-in DomainLab without adding a package.

3. **Independent construction.** Move a pure domain type into the supplied class-library project and run its executable checks.

4. **Diagnose a defect.** Diagnose an API unavailable under a different target framework.

5. **Boundary evidence.** Delete only the lab-owned output directories and verify a clean rebuild.

6. **Transfer and justify.** Design a dependency update review including lock changes, license checks and runtime evidence.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.

For task 4, an API introduced in a newer framework fails to compile under an older `TargetFramework`, with an error saying the member or type cannot be found, even when the installed SDK is newer; read the project file before blaming the code. For task 5, delete only the bin and obj folders inside the lab, then rebuild and confirm restore runs again.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Expose environment facts without overclaiming) before changing anything, and confirm its observation: The running framework generation is compatible with the declared classroom target.
2. Compare Example B (Read the compiled target framework) with Example A and name the first line whose behavior differs. Its observation is: The compiled program reports .NETCoreApp,Version=v10.0, the framework its project targeted, and runs on a .NET 10 runtime.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An SDK version and target framework are related but different.

## Self-check and next step

Say which command first downloads packages, which compiles, and which writes a deployable folder. Distinguish the SDK version from the target framework in your own build output. For task 6, list what a dependency update review records: the version diff, the license, the release notes, and a test run on the new version.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET project SDK and `dotnet` CLI articles describe target frameworks, restore, build, run and publish.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
