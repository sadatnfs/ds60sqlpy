# csharp-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-028_solution.cs](csharp-028_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use independently derived cases:** The literal expectations come from the stated clamp rule, not a duplicated implementation. Negative, zero and positive cases preserve their intended categories.

**Detect a plausible wrong function:** A property complements examples but does not replace the domain-specific expected values. The zero case catches the incorrect default, and clamping twice changes nothing further.

## Reason through the six tasks

1. **Predict and explain.** Explain which wrong implementations each case would reject.

2. **Guided modification.** Add an extreme integer case without overflow.

3. **Independent construction.** Write table-driven checks for your inventory quantity validator.

4. **Diagnose a defect.** Diagnose an assertion comparing a function call with the same call.

5. **Boundary evidence.** Test idempotence and an independently derived boundary value.

6. **Transfer and justify.** Separate unit and integration evidence for a JSON file importer.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A test is useful when a plausible wrong implementation would fail it. Repeating the implementation expression on both sides of an assertion provides weak independence. Start from a contract, choose a normal case, a boundary case and a known misconception, then derive expected outcomes separately.

The classroom uses framework-free throwing checks so the default route needs no package download. A separate prepared project can use a test framework and a test runner. Keep deterministic unit tests focused on pure behavior, and label integration tests that exercise files, databases or networks. A passing unit test does not prove a dependency is configured correctly.

A table of inputs and expected values separates cases from the loop executing them. An exception assertion should check the intended category. Avoid sleep-based timing tests; coordinate concurrent states with explicit signals.

Tests that always print success or catch their own assertion failures provide misleading evidence. A flaky test weakens trust even when production code is correct. Random generation requires a reproducible seed and a clear oracle.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
