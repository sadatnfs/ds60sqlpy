# rust-013: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-013_solution.rs](rust-013_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Render a success payload:** The rendering function borrows the state and extracts only the matching payload. The ready state carries a count rather than an unrelated optional field.

**Render a distinct failure:** The model cannot simultaneously be both ready and failed. Failure preserves its reason and remains a distinct state.

## Reason through the six tasks

1. **Predict and explain.** Identify which payload is valid in each state.

2. **Guided modification.** Add a Loading variant and update every exhaustive consumer.

3. **Independent construction.** Model an import as pending, completed or rejected with state-specific information.

4. **Diagnose a defect.** Diagnose a collection of optional fields that permits contradictory states.

5. **Boundary evidence.** Test every declared variant.

6. **Transfer and justify.** Design valid transitions between states and explain which transitions should be rejected.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An enum represents one case from a declared set. Each case can carry the data relevant to that state. This prevents impossible combinations such as a success flag paired with an error message and no result. Match exposes the state distinction and binds the appropriate payload.

Use enums for meaningful alternatives, not merely to avoid strings. Adding a state requires reviewing transitions and consumers. Exhaustive matching helps the compiler identify affected code. A wildcard may be justified for intentionally open categories, but it weakens feedback when the domain is meant to be closed.

`enum Outcome { Ready(u32), Failed(String) }` declares alternatives. `match value` consumes or borrows according to the matched expression. Matching `&value` can inspect owned payloads without moving them.

Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
