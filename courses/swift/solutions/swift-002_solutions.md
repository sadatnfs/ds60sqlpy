# swift-002: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-002_solution.swift](swift-002_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reassign only mutable state:** The code exposes which part is state and which part is a stable input. The accumulator becomes 8 while the fixed amount remains 4.

**Convert before division:** Converting after integer division would preserve the already truncated result. Integer division yields 3; floating division yields 3.5.

## Reason through the six tasks

1. **Predict and explain.** Identify the inferred type of every binding.

2. **Guided modification.** Replace an unnecessary var with let and explain why it still compiles.

3. **Independent construction.** Compute a mean from an integer total and count using a deliberate conversion.

4. **Diagnose a defect.** Diagnose conversion performed after integer division.

5. **Boundary evidence.** Test an exactly divisible and a non-divisible pair.

6. **Transfer and justify.** Choose units and types for a small measurement model.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Swift distinguishes a binding that may change from one that may not. `let` prevents reassignment; `var` permits it. Prefer let until a state transition is part of the design. The compiler infers types from context, but inference does not make values dynamically typed. A variable initialized with an Int cannot later become a String.

Conversions are explicit between many numeric types. This makes information-changing boundaries visible. A value being representable in one type does not prove it is valid for a domain. Keep units in names and validation at input boundaries. Later chapters introduce reference types, where a constant reference can still point to a mutable object.

`let count: Int = 3` gives an explicit type. `var total = 0` infers Int. `Double(count)` converts a numeric value. Swift source normally does not need semicolons at line ends.

Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
