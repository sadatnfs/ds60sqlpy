# swift-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-011_solution.swift](swift-011_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return two related counts:** The grouping is useful locally without requiring an entire class hierarchy. Named tuple fields expose the accounting relationship.

**Model distinct outcomes:** The switch extracts data after establishing the state case. Each outcome exposes only its own meaningful payload.

## Reason through the six tasks

1. **Predict and explain.** Name the meaning of each tuple field.

2. **Guided modification.** Add a third accounting field only if its meaning is independent.

3. **Independent construction.** Model loading, ready and failed states with an enum.

4. **Diagnose a defect.** Diagnose several optional fields that permit contradictory state combinations.

5. **Boundary evidence.** Add a new enum case and inspect the compiler-reported consumers requiring updates.

6. **Transfer and justify.** Choose tuple or named enum/struct for a reusable public API and explain the tradeoff.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A tuple groups a fixed set of values without introducing a new nominal type. It is useful for local multi-value results, but a named type is clearer when the same concept crosses several APIs. An enum represents one case from a finite set. Associated values attach data relevant only to that case.

Explicit cases prevent impossible combinations such as success=true with an error message and no result. A switch must handle the alternatives. This is a strong foundation for application state machines, parsing results and asynchronous loading state. Add a new case only when it represents a real domain distinction, then review every consumer.

`(count: Int, rejected: Int)` names tuple components. `enum Outcome { case value(Int); case invalid(String) }` binds case-specific payloads. `case .value(let count)` extracts only the matching payload.

An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
