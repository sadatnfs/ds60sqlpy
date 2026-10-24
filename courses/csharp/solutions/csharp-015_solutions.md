# csharp-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-015_solution.cs](csharp-015_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Narrow before using a value:** The bound number is available only after the type pattern succeeds. The same method distinguishes type, value range and string shape.

**Represent results without impossible combinations:** Separate cases prevent a Boolean success flag from disagreeing with unrelated optional fields. Success carries a count; failure carries a reason.

## Reason through the six tasks

1. **Predict and explain.** Predict the matched arm for zero, positive integer, empty text and nonempty text.

2. **Guided modification.** Add a nonempty string arm without shadowing the empty case.

3. **Independent construction.** Model a loading, ready and failed operation with separate payloads.

4. **Diagnose a defect.** Diagnose a broad object arm placed before a more specific case.

5. **Boundary evidence.** Test an unexpected subclass and explain the fallback policy.

6. **Transfer and justify.** Replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Pattern matching combines a test with structured access to the matched data. It can replace a chain of unsafe casts with branches that make the valid shape visible. Patterns are especially useful when a finite set of domain states carries different information, such as loading, success and failure. The goal is a truthful state model, not clever syntax.

A fallback branch should have a deliberate meaning. If a new domain state is introduced later, silently treating it as success is dangerous. C# class hierarchies are not fully closed algebraic data types, so review exhaustiveness and reject unexpected cases explicitly when necessary. Keep missing information distinct from failure information.

`value is int number` tests and binds. Property patterns inspect named properties. A switch expression can select an expression by type and guard. `when` adds a condition after the structural match.

An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
