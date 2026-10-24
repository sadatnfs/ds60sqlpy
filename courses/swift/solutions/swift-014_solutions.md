# swift-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-014_solution.swift](swift-014_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Derive instead of duplicating:** One source of truth prevents stale duplicated state. Area changes with width without a separately updated area field.

**Expose a conversion property:** A computed property can expose a convenient representation while retaining one stored unit. The getter and setter translate between temperature scales.

## Reason through the six tasks

1. **Predict and explain.** Trace which properties are stored and which are derived.

2. **Guided modification.** Add a computed rectangle perimeter.

3. **Independent construction.** Build a value model with one stored unit and a documented converted view.

4. **Diagnose a defect.** Diagnose a separately stored area that is not updated after width changes.

5. **Boundary evidence.** Test zero and a non-integer conversion case.

6. **Transfer and justify.** Choose an explicit method instead of a setter for a state change with validation and failure.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A stored property retains data; a computed property derives a value from other state. Prefer deriving cheap dependent values instead of storing duplicates that can disagree. A property observer reacts to a stored-value change but should not become an invisible substitute for a clear domain operation.

Computed setters translate an external representation back into stored state. That translation may lose information, so document it. Access control can permit reading without external writing. Property wrappers later package reusable access behavior, but start by understanding the plain getter and setter contract.

`var area: Int { width * height }` computes a value. `get` and `set` define two-way access; newValue names the assigned value. didSet observes assignments after the new value is stored.

Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
