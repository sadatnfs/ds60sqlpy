# csharp-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-015_solution.cs](csharp-015_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Narrow before using a value:** The bound number is available only after the type pattern succeeds. The same method distinguishes type, value range and string shape.

**Represent results without impossible combinations:** Separate cases prevent a Boolean success flag from disagreeing with unrelated optional fields. Success carries a count; failure carries a reason.

## Task answers

### Task 1: Predict and explain

Predict the matched arm for zero, positive integer, empty text and nonempty text.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The bound number is available only after the type pattern succeeds. The same method distinguishes type, value range and string shape.

### Task 2: Guided modification

Add a nonempty string arm without shadowing the empty case.

No separate reference answer has been written for this task. Start from Example B: Separate cases prevent a Boolean success flag from disagreeing with unrelated optional fields. Success carries a count; failure carries a reason.

### Task 3: Independent construction

Model a loading, ready and failed operation with separate payloads.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Pattern** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose a broad object arm placed before a more specific case.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.

### Task 5: Boundary evidence

Test an unexpected subclass and explain the fallback policy.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Narrow before using a value) and Example B (Represent results without impossible combinations).

### Task 6: Transfer and justify

Replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Pattern**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Pattern matching combines a test with structured access to the matched data. It can replace a chain of unsafe casts with branches that make the valid shape visible. Patterns are especially useful when a finite set of domain states carries different information, such as loading, success and failure. The goal is a truthful state model, not clever syntax.

A fallback branch should have a deliberate meaning. If a new domain state is introduced later, silently treating it as success is dangerous. C# class hierarchies are not fully closed algebraic data types, so review exhaustiveness and reject unexpected cases explicitly when necessary. Keep missing information distinct from failure information.

`value is int number` tests and binds. Property patterns inspect named properties. A switch expression can select an expression by type and guard. `when` adds a condition after the structural match.

An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.

## Review before continuing

Run the reference and confirm that it prints `csharp-015: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
