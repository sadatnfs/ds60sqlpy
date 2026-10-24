# swift-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-005_solution.swift](swift-005_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve zero as a value:** The branch proves presence before the wrapped integer is used. A present zero remains distinct from nil.

**Parse with an absence policy:** The fallback is an explicit display sentinel in this fixture, not a valid quantity. Parsing produces an optional and malformed text is absent.

## Reason through the six tasks

1. **Predict and explain.** Explain the difference between nil and a wrapped zero.

2. **Guided modification.** Replace the display sentinel with an unknown label.

3. **Independent construction.** Write a parser accepting only present nonnegative integers.

4. **Diagnose a defect.** Diagnose force-unwrapping malformed external text.

5. **Boundary evidence.** Test empty, zero, negative and out-of-range input.

6. **Transfer and justify.** Model an optional measurement whose absence must survive serialization and reporting.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An optional represents either a wrapped value or no value. This makes absence part of the type rather than an undocumented sentinel. Int zero can be a real measurement, so it should not also mean missing. Optional binding introduces a nonoptional value only inside the branch where presence has been established.

A force unwrap asserts that absence is impossible and traps if that assertion is wrong. It is suitable for tightly controlled fixture literals but is usually a poor external-input policy. Prefer if let for branching and guard let for an early-exit precondition. A fallback with ?? is valid only when the domain really assigns that replacement meaning.

`Int?` abbreviates Optional<Int>. `if let value = optional` unwraps on the present branch. `guard let` requires an early exit on failure. `??` selects a fallback only when the optional is nil.

Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
