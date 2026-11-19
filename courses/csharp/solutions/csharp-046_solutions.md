# csharp-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-046_solution.cs](csharp-046_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a target-typed collection:** The compact syntax still creates concrete storage according to its target. The target types select array and list representations.

**Keep constructor policy visible:** Concise construction should preserve a clear relationship between input parameters and behavior. The three newer checks compile only with C# 13 or 14, which the net10.0 target selects by default; an older target would reject them at compile time. The supplied factor is used by the instance operation, nameof(List<>) is List, missing?.Capacity = 32 leaves the null builder alone, and \e is the escape character.

## Task answers

### Task 1: Predict and explain

Identify the target type of each collection expression.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The compact syntax still creates concrete storage according to its target. The target types select array and list representations.

### Task 2: Guided modification

Use an empty collection expression with an explicit target.

No separate reference answer has been written for this task. Start from Example B: Concise construction should preserve a clear relationship between input parameters and behavior. The three newer checks compile only with C# 13 or 14, which the net10.0 target selects by default; an older target would reject them at compile time. The supplied factor is used by the instance operation, nameof(List<>) is List, missing?.Capacity = 32 leaves the null builder alone, and \e is the escape character.

### Task 3: Independent construction

Refactor one simple class to a primary constructor without changing behavior.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Language version** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose copying new syntax into a project targeting an older language version.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.

### Task 5: Boundary evidence

Test empty spread and zero scaling.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use a target-typed collection) and Example B (Keep constructor policy visible).

### Task 6: Transfer and justify

Review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Language version**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Language evolution adds concise ways to express familiar contracts. Primary constructors, collection expressions and improved patterns can reduce noise, but unfamiliar syntax should be introduced by its meaning rather than used to make code look advanced. Version-aware code records the target language generation and avoids accidentally relying on a preview feature.

C# 14 accompanies .NET 10 and is the default for the classroom's net10.0 target. C# 13 (.NET 9) added params collections, the System.Threading.Lock type for lock statements and the \e escape sequence. C# 14 adds the field keyword in property accessors, extension members, null-conditional assignment such as a?.B = c, nameof for unbound generic types such as List<> and implicit span conversions. Example B exercises three of these features. New syntax does not relax nullability, ownership or equality rules. A code review should ask whether a feature makes the domain relationship easier to see and whether contributors can diagnose its errors.

A collection expression such as `[1, 2, 3]` is target-typed. A primary constructor supplies parameters used by members. `nameof` produces a symbol name while retaining compile-time refactoring support; since C# 14 it also accepts an unbound generic type such as `nameof(List<>)`. `missing?.Capacity = 32` assigns only when `missing` is not null, and `\e` is the escape character U+001B.

Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.

## Review before continuing

Run the reference and confirm that it prints `csharp-046: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
