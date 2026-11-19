# swift-033: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-033_solution.swift](swift-033_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Send an immutable snapshot:** No mutable object identity is shared across the boundary. The task receives immutable value data and returns 6.

**Return values to the owner:** Child tasks produce values instead of concurrently mutating one array. The parent owns result aggregation and sorts it deterministically.

## Task answers

### Task 1: Predict and explain

Identify the owner of every value crossing a task boundary.

No separate reference answer has been written for this task. Example A is the evidence to compare with: No mutable object identity is shared across the boundary. The task receives immutable value data and returns 6.

### Task 2: Guided modification

Add another immutable field to the snapshot.

No separate reference answer has been written for this task. Start from Example B: Child tasks produce values instead of concurrently mutating one array. The parent owns result aggregation and sorts it deterministically.

### Task 3: Independent construction

Replace a shared mutable result class with a sendable value result.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct Summary: Sendable {
  let count: Int
  let total: Int
}
let summary = await Task { () -> Summary in
  let values = [2, 3, 4]
  return Summary(count: values.count, total: values.reduce(0, +))
}.value
precondition(summary.count == 3 && summary.total == 9)
```

**Observe:** The task returns Summary(count: 3, total: 9).

The result is an immutable Sendable value returned by the task, so no shared mutable object crosses the concurrency boundary.

### Task 4: Diagnose a defect

Diagnose an unchecked Sendable annotation hiding unsynchronized mutable state.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.

### Task 5: Boundary evidence

Test empty snapshots and multiple concurrent producers.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Send an immutable snapshot) and Example B (Return values to the owner).

### Task 6: Transfer and justify

Design data exchange between a UI model and a background actor using immutable snapshots.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Sendable**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Sendable describes values that can cross concurrency boundaries without introducing unsafe shared mutation. Immutable structs composed of sendable members are a natural fit. A mutable reference type requires a real synchronization or isolation story; adding unchecked Sendable only removes the compiler's protection and transfers responsibility to the programmer.

Swift 6 checking makes many previously implicit assumptions visible. Treat diagnostics as design feedback: identify the owner of each mutable value and the boundary across which it moves. A MainActor-isolated UI model and a background actor can exchange immutable snapshots instead of sharing writable object graphs. This is both a language rule and an architecture technique.

`struct Snapshot: Sendable` declares a crossing contract. Actor calls and child tasks create concurrency boundaries. Capture immutable values and return results instead of mutating shared containers from several tasks.

Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.

## Review before continuing

Run the reference and confirm that it prints `swift-033: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
