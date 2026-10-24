# csharp-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-043_solution.cs](csharp-043_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Expose environment facts without overclaiming:** Runtime facts are useful diagnostics but do not replace a source and project review. The running framework generation is compatible with the declared classroom target.

**Keep configuration explicit:** A real project fixture, rather than this metadata demonstration, is required to qualify multi-file build behavior. The example preserves the intended target and nullable policy.

## Reason through the six tasks

1. **Predict and explain.** Explain the distinct purpose of restore, build, run and publish.

2. **Guided modification.** Build the checked-in DomainLab without adding a package.

3. **Independent construction.** Move a pure domain type into the supplied class-library project and run its executable checks.

4. **Diagnose a defect.** Diagnose an API unavailable under a different target framework.

5. **Boundary evidence.** Delete only the lab-owned output directories and verify a clean rebuild.

6. **Transfer and justify.** Design a dependency update review including lock changes, license checks and runtime evidence.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A project file records the compilation target and build policy. Source that compiles against one framework can fail against another if it uses unavailable APIs. Pin a supported SDK policy and target framework deliberately. Package references add another versioned dependency surface, including transitive dependencies and restore behavior.

The classroom builds a fixed net10.0 project without arbitrary packages. External multi-file labs teach the project workflow explicitly: restore during preparation, build without changing dependencies, run tests, then publish a selected artifact. A portable build does not prove every architecture or operating system works. Keep actual build and runtime evidence separate.

`TargetFramework` selects net10.0. Nullable and ImplicitUsings are compile policies. `dotnet restore`, `dotnet build --no-restore`, `dotnet run --no-build` and `dotnet publish` have distinct responsibilities.

An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
