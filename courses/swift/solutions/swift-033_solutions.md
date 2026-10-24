# swift-033: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-033_solution.swift](swift-033_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Send an immutable snapshot:** No mutable object identity is shared across the boundary. The task receives immutable value data and returns 6.

**Return values to the owner:** Child tasks produce values instead of concurrently mutating one array. The parent owns result aggregation and sorts it deterministically.

## Reason through the six tasks

1. **Predict and explain.** Identify the owner of every value crossing a task boundary.

2. **Guided modification.** Add another immutable field to the snapshot.

3. **Independent construction.** Replace a shared mutable result class with a sendable value result.

4. **Diagnose a defect.** Diagnose an unchecked Sendable annotation hiding unsynchronized mutable state.

5. **Boundary evidence.** Test empty snapshots and multiple concurrent producers.

6. **Transfer and justify.** Design data exchange between a UI model and a background actor using immutable snapshots.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Sendable describes values that can cross concurrency boundaries without introducing unsafe shared mutation. Immutable structs composed of sendable members are a natural fit. A mutable reference type requires a real synchronization or isolation story; adding unchecked Sendable only removes the compiler's protection and transfers responsibility to the programmer.

Swift 6 checking makes many previously implicit assumptions visible. Treat diagnostics as design feedback: identify the owner of each mutable value and the boundary across which it moves. A MainActor-isolated UI model and a background actor can exchange immutable snapshots instead of sharing writable object graphs. This is both a language rule and an architecture technique.

`struct Snapshot: Sendable` declares a crossing contract. Actor calls and child tasks create concurrency boundaries. Capture immutable values and return results instead of mutating shared containers from several tasks.

Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
