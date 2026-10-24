# csharp-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-046_solution.cs](csharp-046_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a target-typed collection:** The compact syntax still creates concrete storage according to its target. The target types select array and list representations.

**Keep constructor policy visible:** Concise construction should preserve a clear relationship between input parameters and behavior. The supplied factor is used by the instance operation.

## Reason through the six tasks

1. **Predict and explain.** Identify the target type of each collection expression.

2. **Guided modification.** Use an empty collection expression with an explicit target.

3. **Independent construction.** Refactor one simple class to a primary constructor without changing behavior.

4. **Diagnose a defect.** Diagnose copying new syntax into a project targeting an older language version.

5. **Boundary evidence.** Test empty spread and zero scaling.

6. **Transfer and justify.** Review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Language evolution adds concise ways to express familiar contracts. Primary constructors, collection expressions and improved patterns can reduce noise, but unfamiliar syntax should be introduced by its meaning rather than used to make code look advanced. Version-aware code records the target language generation and avoids accidentally relying on a preview feature.

C# 14 accompanies .NET 10. This chapter uses established modern features supported by that target and explains the broader C# 14 release boundary through official documentation. New syntax does not relax nullability, ownership or equality rules. A code review should ask whether a feature makes the domain relationship easier to see and whether contributors can diagnose its errors.

A collection expression such as `[1, 2, 3]` is target-typed. A primary constructor supplies parameters used by members. `nameof` produces a symbol name while retaining compile-time refactoring support.

Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
