# swift-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-031_solution.swift](swift-031_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Serialize increments:** The actor owns mutation, while child tasks send requests rather than sharing a writable integer. All twenty increments are retained.

**Keep a reservation atomic within the actor:** The check and update contain no suspension, preserving the invariant as one actor operation. The second reservation is rejected without making stock negative.

## Task answers

### Task 1: Predict and explain

Identify every actor-isolated read and write.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The actor owns mutation, while child tasks send requests rather than sharing a writable integer. All twenty increments are retained.

### Task 2: Guided modification

Add a read-only snapshot method returning a value type.

No separate reference answer has been written for this task. Start from Example B: The check and update contain no suspension, preserving the invariant as one actor operation. The second reservation is rejected without making stock negative.

### Task 3: Independent construction

Implement a bounded actor-owned queue with explicit admission.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
actor BoundedQueue {
  private var items: [Int] = []
  let capacity: Int
  init(capacity: Int) { self.capacity = capacity }
  func offer(_ item: Int) -> Bool {
    guard items.count < capacity else { return false }
    items.append(item)
    return true
  }
  func take() -> Int? { items.isEmpty ? nil : items.removeFirst() }
}
let queue = BoundedQueue(capacity: 2)
let admitted = [await queue.offer(1), await queue.offer(2), await queue.offer(3)]
precondition(admitted == [true, true, false])
let first = await queue.take()
precondition(first == 1)
```

**Observe:** Two offers are admitted, the third is refused, and the first item taken is 1.

The actor serializes every offer and take, so the capacity check and the append can never interleave with another caller.

### Task 4: Diagnose a defect

Diagnose checking stock, awaiting another operation and then subtracting without revalidation.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.

### Task 5: Boundary evidence

Test zero and excess reservations.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Serialize increments) and Example B (Keep a reservation atomic within the actor).

### Task 6: Transfer and justify

Design a reservation state machine for an operation requiring external I/O before commitment.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Actor isolation**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An actor isolates mutable state so asynchronous callers cannot directly access it without crossing the actor boundary. This prevents many data races by making ownership part of the type system. Actor methods can still contain logical races: when an operation suspends, another task may enter and change state before it resumes.

Keep a state transition synchronous inside the actor whenever possible. If an operation must await external work, revalidate assumptions after suspension or model a reservation explicitly. Actors provide isolation, not an automatic transaction across every await. Sendable describes which values can safely cross concurrency boundaries.

`actor CounterActor` owns isolated state. Calls from outside use await even when the method body itself does not suspend. Read an actor result into a local value before passing it to precondition, whose autoclosure is synchronous.

Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.

## Review before continuing

Run the reference and confirm that it prints `swift-031: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
