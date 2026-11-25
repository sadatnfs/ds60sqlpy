# swift-031: explanation and comparison

Reference program: [swift-031_solution.swift](swift-031_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Serialize increments:** The actor owns mutation, while child tasks send requests rather than sharing a writable integer. All twenty increments are retained.

**Keep a reservation atomic within the actor:** The check and update contain no suspension, preserving the invariant as one actor operation. The second reservation is rejected without making stock negative.

## Task answers

### Task 1: Predict and explain

Identify every actor-isolated read and write.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let inventory = InventoryActor(stock: 3)
let before = await inventory.stock
let reserved = await inventory.reserve(1)
let after = await inventory.stock
precondition(before == 3 && reserved && after == 2)
```

**Observe:** The outside reads of stock and the reserve call each need await, and stock goes from 3 to 2.

stock is actor-isolated, so every outside read is an await; inside reserve, the guard read and the subtraction run on the actor without suspension, forming one serialized step.

### Task 2: Guided modification

Add a read-only snapshot method returning a value type.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let inventory = InventoryActor(stock: 3)
let before = await inventory.snapshot()
_ = await inventory.reserve(2)
let after = await inventory.snapshot()
precondition(before == StockSnapshot(stock: 3) && after.stock == 1)
```

**Observe:** The snapshot taken before the reservation still says 3, and a later one says 1.

snapshot returns a Sendable value copy, so the caller holds a stable record that later actor changes cannot alter.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
actor SplitInventory {
  private(set) var stock = 2
  func canReserve(_ amount: Int) -> Bool { amount <= stock }
  func subtract(_ amount: Int) { stock -= amount }
}
let split = SplitInventory()
let firstCheck = await split.canReserve(2)
let secondCheck = await split.canReserve(2)
await split.subtract(2)
await split.subtract(2)
let leftover = await split.stock
precondition(firstCheck && secondCheck && leftover == -2)
let safe = InventoryActor(stock: 2)
let one = await safe.reserve(2)
let two = await safe.reserve(2)
precondition(one && !two)
```

**Observe:** Two callers both pass the separate check and stock falls to -2; InventoryActor rejects the second reservation.

Each actor call is serialized, but the await between check and subtract lets other work interleave. Keeping the check and the write in one actor method with no await inside removes the gap.

### Task 5: Boundary evidence

Test zero and excess reservations.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let inventory = InventoryActor(stock: 3)
let zero = await inventory.reserve(0)
let excess = await inventory.reserve(4)
let exact = await inventory.reserve(3)
let remaining = await inventory.stock
precondition(zero && !excess && exact && remaining == 0)
```

**Observe:** Reserving 0 succeeds, 4 is refused, and exactly 3 succeeds and leaves 0.

The guard admits amounts from 0 through stock inclusive, so only the excess request fails and it changes nothing.

### Task 6: Transfer and justify

Design a reservation state machine for an operation requiring external I/O before commitment.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `CounterActor` owns an integer and twenty child tasks each await `increment()`. `InventoryActor` performs its whole check-and-subtract inside one synchronous actor method. Example B reserves 2 twice from stock 3. The task 3 answer is an actor-owned queue with explicit admission.

**Why it is correct.** Actor methods run one at a time on the actor's executor, so twenty increments produce exactly 20 with no lost updates. `reserve` contains no `await`, so no other call can run between the guard and the subtraction: the first request leaves 1 and the second is refused because 2 exceeds 1. In task 3 two offers are admitted, the third is refused, and the first item taken is 1.

**A plausible wrong approach.** Splitting reservation into `let ok = await inventory.canReserve(2)` followed by `await inventory.subtract(2)` reintroduces the race task 4 describes: two callers can both see stock 3 and both subtract, leaving -1. Each call is isolated, but the two-step workflow is not.

**How to verify.** Change the counter to a plain class shared by the twenty tasks in a scratch pad and read the Swift 6 diagnostic about sending a non-Sendable value. For task 5, reserve 0 (succeeds, stock unchanged) and reserve 4 from 3 (refused).

## Mechanism and diagnostic reasoning

An actor isolates mutable state so asynchronous callers cannot directly access it without crossing the actor boundary. This prevents many data races by making ownership part of the type system. Actor methods can still contain logical races: when an operation suspends, another task may enter and change state before it resumes.

Keep a state transition synchronous inside the actor whenever possible. If an operation must await external work, revalidate assumptions after suspension or model a reservation explicitly. Actors provide isolation, not an automatic transaction across every await. Sendable describes which values can safely cross concurrency boundaries.

`actor CounterActor` owns isolated state. Calls from outside use await even when the method body itself does not suspend. Read an actor result into a local value before passing it to precondition, whose autoclosure is synchronous.

Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.

## Review before continuing

Run the reference and confirm it prints `swift-031: passed`, then rerun the guide's counterexample.
