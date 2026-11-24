# csharp-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-043_solution.cs](csharp-043_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Expose environment facts without overclaiming:** Runtime facts are useful diagnostics but do not replace a source and project review. The running framework generation is compatible with the declared classroom target.

**Read the compiled target framework:** Both values come from the build and the runtime rather than from a hand-written table, so the checks fail if the project targets another framework. A real multi-project fixture is still required to qualify restore and publish behavior. The compiled program reports .NETCoreApp,Version=v10.0, the framework its project targeted, and runs on a .NET 10 runtime.

## Task answers

### Task 1: Predict and explain

Explain the distinct purpose of restore, build, run and publish.

**Written answer.** `dotnet restore` resolves the projects' package and framework references into `obj/project.assets.json` from the configured feeds. `dotnet build` compiles against those resolved assets into `bin`, and fails with NETSDK1004 if the assets file is missing. `dotnet run` builds if needed and then starts the program; with `--no-build` it only runs the existing output. `dotnet publish` produces a deployable folder for a chosen configuration and, optionally, a runtime identifier. In the worker image the DomainLab sequence was: restore exit 0, build exit 0 with 0 warnings and 0 errors, run printed `DomainLab: seven contract checks passed`.

**Why it is correct.** Each command can fail for a different reason: restore for feeds and versions, build for code, run for behavior, publish for deployment shape. Knowing which step failed tells you where to look.

**Plausible wrong approach.** Reading a successful restore as a successful build, or a successful build as passing checks, skips the evidence each later step provides.

**How to verify.** Delete `obj`, run `dotnet build --no-restore` and see NETSDK1004, then restore and build again.

### Task 2: Guided modification

Build the checked-in DomainLab without adding a package.

**Written answer.** DomainLab is two projects: `Domain` is a class library and `Checks` is an executable that references it, with a local `NuGet.Config`. Built offline in the csharp worker image (SDK 10.0.404, `--network none`) with no package added: `dotnet restore Checks/Checks.csproj --configfile NuGet.Config` exit 0; `dotnet build Checks/Checks.csproj --no-restore` exit 0 with 0 warnings and 0 errors, which also built `Domain` through the project reference; `dotnet run --project Checks/Checks.csproj --no-build` printed `DomainLab: seven contract checks passed` with exit 0.

**Why it is correct.** Building through the executable proves both projects compile and the reference is correct, and running the checks proves the behavior, not just the compilation.

**Plausible wrong approach.** Adding a package to make something build, or running `dotnet build` on only `Domain`, changes or skips the thing the task asks you to verify.

**How to verify.** Run the three commands yourself and confirm the same exit codes and the exact `seven contract checks passed` line.

### Task 3: Independent construction

Move a pure domain type into the supplied class-library project and run its executable checks.

**Written answer.** A pure domain type has no input or output of its own, so it belongs in `Domain`. The reference moved this rule into `Domain/RestockRule.cs`:

```csharp
namespace Journey.Domain;

public sealed record RestockRule(string Name, int Minimum) {
  public bool Needs(Report report) {
    ArgumentNullException.ThrowIfNull(report);
    report.Totals.TryGetValue(Name, out int total);
    return total < Minimum;
  }
}
```

and added three checks to `Checks/Program.cs`: pear with total 6 does not need restocking at minimum 5, apple with total 3 does, and a missing item counts as 0. In the worker image, `grep Console Domain/*.cs` found nothing, the rebuild succeeded with 0 warnings, and the run printed `DomainLab: ten contract checks passed`.

**Why it is correct.** The library stays reusable and testable only if it depends on nothing above it. The executable may depend on the library, never the reverse.

**Plausible wrong approach.** Putting `Console.WriteLine` inside the rule, or referencing `Checks` from `Domain`, makes the core depend on one particular program and creates a circular reference.

**How to verify.** Search `Domain` for `Console`, `File` and `Environment` and confirm none appear, then run the checks and see the new count.

### Task 4: Diagnose a defect

Diagnose an API unavailable under a different target framework.

**Written answer.** DomainLab targets `net10.0`, and Example B confirms the compiled framework is `.NETCoreApp,Version=v10.0`. An API added in a later framework, such as `System.Threading.Lock` from .NET 9, does not exist in the `net8.0` reference assemblies, so retargeting a project that uses it fails to compile with CS0246 (type not found) or CS0117 (member not found), not at run time. In the offline worker image the retarget fails even earlier: `dotnet restore` reports NU1100 `Unable to resolve 'Microsoft.NETCore.App.Ref (= 8.0.34)' for 'net8.0'`, because the net8.0 targeting pack is not in the local feed. Diagnose by reading the error code first: NU means restore, CS means compile.

**Why it is correct.** The target framework decides which API surface the compiler sees. The SDK version only decides which tools are running.

**Plausible wrong approach.** Upgrading the SDK, or assuming that because the program runs on a .NET 10 runtime it can use any .NET 10 API while targeting `net8.0`, confuses the SDK and runtime with the target.

**How to verify.** Check the `<TargetFramework>` in each `.csproj`, then guard a newer API with `#if NET9_0_OR_GREATER` or keep the target at `net10.0`.

### Task 5: Boundary evidence

Delete only the lab-owned output directories and verify a clean rebuild.

**Written answer.** The lab-owned outputs are exactly `Checks/bin`, `Checks/obj`, `Domain/bin` and `Domain/obj`. In the worker image, after deleting those four with `rm -rf`, no `bin` or `obj` directory remained and the SHA-256 list of every `.cs`, `.csproj` and `NuGet.Config` file was identical before and after (`cmp` exit 0). `dotnet build --no-restore` then failed with NETSDK1004 because `obj/project.assets.json` was gone, which is expected; after `dotnet restore --configfile NuGet.Config` the build succeeded with 0 warnings and the run printed the same passing line as before.

**Why it is correct.** A clean rebuild proves the result comes from the sources and configuration in the repository, not from stale outputs left by an earlier build.

**Plausible wrong approach.** Running `git clean -fdx` or deleting a home-directory NuGet cache removes files the task does not own and can destroy unrelated work.

**How to verify.** Record source hashes, delete only the four output folders, restore, build and run, and confirm the hashes match and the checks pass.

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
