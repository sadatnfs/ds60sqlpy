# swift-033: explanation and comparison

Reference program: [swift-033_solution.swift](swift-033_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Send an immutable snapshot:** No mutable object identity is shared across the boundary. The task receives immutable value data and returns 6.

**Return values to the owner:** Child tasks produce values instead of concurrently mutating one array. The parent owns result aggregation and sorts it deterministically.

## Task answers

### Task 1: Predict and explain

Identify the owner of every value crossing a task boundary.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let snapshot = Snapshot(name: "pear", quantity: 3)
let task = Task { Snapshot(name: snapshot.name, quantity: snapshot.quantity * 2) }
let doubled = await task.value
precondition(snapshot.quantity == 3)
precondition(doubled.name == "pear" && doubled.quantity == 6)
```

**Observe:** The parent's snapshot still holds 3, and the task hands back a new snapshot holding 6.

The parent owns snapshot and the task receives an immutable copy; the task owns the value it builds until it returns, and then the awaiting parent owns the result.

### Task 2: Guided modification

Add another immutable field to the snapshot.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
struct PricedSnapshot: Sendable {
  let name: String
  let quantity: Int
  let unitPrice: Int
}
let snapshot = PricedSnapshot(name: "pear", quantity: 3, unitPrice: 4)
let cost = await Task { snapshot.quantity * snapshot.unitPrice }.value
precondition(cost == 12)
```

**Observe:** With an added unitPrice of 4, the task computes a cost of 12 from 3 pears.

A struct whose stored properties are all let and themselves Sendable stays Sendable, so the new field crosses the task boundary without any extra synchronization.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
actor Tally {
  private(set) var count = 0
  func add() { count += 1 }
}
let tally = Tally()
await withTaskGroup(of: Void.self) { group in
  for _ in 0..<100 { group.addTask { await tally.add() } }
}
let count = await tally.count
precondition(count == 100)
```

**Observe:** One hundred concurrent increments through the actor produce exactly 100.

Marking a class with a mutable var as @unchecked Sendable silences the compiler without adding any lock, so concurrent increments can be lost. Moving the state into an actor makes the compiler enforce serialized access instead.

### Task 5: Boundary evidence

Test empty snapshots and multiple concurrent producers.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let none = await withTaskGroup(of: Snapshot.self, returning: [Snapshot].self) { group in
  var collected: [Snapshot] = []
  for await value in group { collected.append(value) }
  return collected
}
precondition(none.isEmpty)
let many = await withTaskGroup(of: Snapshot.self, returning: [String].self) { group in
  for number in 1...4 { group.addTask { Snapshot(name: "p\(number)", quantity: number) } }
  var names: [String] = []
  for await value in group { names.append(value.name) }
  return names.sorted()
}
precondition(many == ["p1", "p2", "p3", "p4"])
```

**Observe:** A group with no producers returns no snapshots, and four producers yield p1 through p4 once sorted.

The parent alone appends and sorts, so the result is deterministic regardless of which producer finishes first, and the empty case needs no special handling.

### Task 6: Transfer and justify

Design data exchange between a UI model and a background actor using immutable snapshots.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `Snapshot` is a struct with only `let` fields and an explicit `Sendable` conformance. Example A captures one snapshot in a `Task` and doubles its quantity. Example B has two children each return a new snapshot, and the parent collects and sorts them by name. The task 3 answer replaces a shared mutable result class with a sendable summary value.

**Why it is correct.** A struct of immutable String and Int fields has no shared mutable state, so sending it to a task is safe and the compiler accepts it under strict checking. The task reads quantity 3 and returns 6. Children in Example B return values, and only the parent appends, so sorting by name gives `["a", "b"]` regardless of completion order. Task 3 returns `Summary(count: 3, total: 9)`.

**A plausible wrong approach.** Marking a class with a mutable array as `@unchecked Sendable` so the diagnostic disappears is the task 4 defect: the compiler stops checking, but two tasks can still append at once and corrupt the array. The annotation promises an invariant that the code does not provide.

**How to verify.** Change one `let` in `Snapshot` to `var` and confirm it still compiles, since a value-type copy remains safe; then change the struct to a non-final class and read the Sendable diagnostic. For task 5, run a group with no children and confirm an empty array.

## Mechanism and diagnostic reasoning

Sendable describes values that can cross concurrency boundaries without introducing unsafe shared mutation. Immutable structs composed of sendable members are a natural fit. A mutable reference type requires a real synchronization or isolation story; adding unchecked Sendable only removes the compiler's protection and transfers responsibility to the programmer.

Swift 6 checking makes many previously implicit assumptions visible. Treat diagnostics as design feedback: identify the owner of each mutable value and the boundary across which it moves. A MainActor-isolated UI model and a background actor can exchange immutable snapshots instead of sharing writable object graphs. This is both a language rule and an architecture technique.

`struct Snapshot: Sendable` declares a crossing contract. Actor calls and child tasks create concurrency boundaries. Capture immutable values and return results instead of mutating shared containers from several tasks.

Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.

## Review before continuing

Run the reference and confirm it prints `swift-033: passed`, then rerun the guide's counterexample.
