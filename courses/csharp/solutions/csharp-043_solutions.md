# csharp-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-043_solution.cs](csharp-043_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Expose environment facts without overclaiming:** Runtime facts are useful diagnostics but do not replace a source and project review. The running framework generation is compatible with the declared classroom target.

**Read the compiled target framework:** Both values come from the build and the runtime rather than from a hand-written table, so the checks fail if the project targets another framework. A real multi-project fixture is still required to qualify restore and publish behavior. The compiled program reports .NETCoreApp,Version=v10.0, the framework its project targeted, and runs on a .NET 10 runtime.

## Task answers

### Task 1: Predict and explain

Explain the distinct purpose of restore, build, run and publish.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Runtime facts are useful diagnostics but do not replace a source and project review. The running framework generation is compatible with the declared classroom target.

### Task 2: Guided modification

Build the checked-in DomainLab without adding a package.

No separate reference answer has been written for this task. Start from Example B: Both values come from the build and the runtime rather than from a hand-written table, so the checks fail if the project targets another framework. A real multi-project fixture is still required to qualify restore and publish behavior. The compiled program reports .NETCoreApp,Version=v10.0, the framework its project targeted, and runs on a .NET 10 runtime.

### Task 3: Independent construction

Move a pure domain type into the supplied class-library project and run its executable checks.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Target framework** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose an API unavailable under a different target framework.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.

### Task 5: Boundary evidence

Delete only the lab-owned output directories and verify a clean rebuild.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Expose environment facts without overclaiming) and Example B (Read the compiled target framework).

### Task 6: Transfer and justify

Design a dependency update review including lock changes, license checks and runtime evidence.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Target framework**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A project file records the compilation target and build policy. Source that compiles against one framework can fail against another if it uses unavailable APIs. Pin a supported SDK policy and target framework deliberately. Package references add another versioned dependency surface, including transitive dependencies and restore behavior.

The classroom builds a fixed net10.0 project without arbitrary packages. External multi-file labs teach the project workflow explicitly: restore during preparation, build without changing dependencies, run tests, then publish a selected artifact. A portable build does not prove every architecture or operating system works. Keep actual build and runtime evidence separate.

`TargetFramework` selects net10.0. Nullable and ImplicitUsings are compile policies. `dotnet restore`, `dotnet build --no-restore`, `dotnet run --no-build` and `dotnet publish` have distinct responsibilities.

An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.

## Review before continuing

Run the reference and confirm that it prints `csharp-043: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
