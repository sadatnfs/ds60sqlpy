# csharp-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-011_solution.cs](csharp-011_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Carry absence through a computation:** Conditional access propagates missing information until a boundary deliberately chooses a display representation. The optional length is absent, not zero.

**Distinguish zero from missing:** Pattern matching unwraps only the present case, giving a nonnullable variable inside that branch. A measured zero and an unknown measurement produce distinct descriptions.

## Reason through the six tasks

1. **Predict and explain.** Predict nullable length and its fallback for null and empty text.

2. **Guided modification.** Use a visible unknown label rather than a numeric sentinel.

3. **Independent construction.** Write a formatter preserving missing, zero and positive measurements.

4. **Diagnose a defect.** Diagnose using ! to suppress a warning on an actually null value.

5. **Boundary evidence.** Test whitespace-only text separately from null and empty text.

6. **Transfer and justify.** Design an import field whose missing value has different meaning from an explicit zero or empty value.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Missing information should be visible in a type and a control-flow policy. Nullable reference annotations let the compiler warn when a value may be null; they are static analysis, not a new runtime container. An annotation cannot validate data arriving from another language, reflection or an external format. Keep runtime validation where that data enters.

A nullable value type such as int? represents either an int or no value. Choosing a fallback is a domain decision. Replacing missing age with zero means something very different from reporting unknown age. Prefer explicit branches when a default would blur those meanings.

`string?` permits null in static analysis; `int?` is Nullable<int>. `?.` conditionally accesses a member and preserves absence. `??` supplies a fallback. The null-forgiving operator `!` silences analysis but performs no check.

A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
