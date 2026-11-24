# swift-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-029_solution.swift](swift-029_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Collect results without assuming order:** Independent values cross the boundary, and the parent alone mutates the result array. Sorted results are deterministic despite unspecified completion order.

**Handle an empty group:** The empty path needs no special background work or timer. No admitted children produces the identity result zero.

## Task answers

### Task 1: Predict and explain

Identify who owns each task and the result array.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let values = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
  for value in [1, 2, 3] { group.addTask { value * 2 } }
  var owned: [Int] = []
  for await result in group { owned.append(result) }
  return owned
}
precondition(values.count == 3 && values.sorted() == [2, 4, 6])
```

**Observe:** The group returns three results that sort to [2, 4, 6].

The group owns the three child tasks and does not return until they finish; each child owns only its copy of value, and only the parent closure owns and appends to the array.

### Task 2: Guided modification

Attach input indices and reconstruct submission ordering.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let inputs = [3, 1, 2]
let ordered = await withTaskGroup(of: (Int, Int).self, returning: [Int].self) { group in
  for (index, value) in inputs.enumerated() { group.addTask { (index, value * 2) } }
  var pairs: [(Int, Int)] = []
  for await pair in group { pairs.append(pair) }
  return pairs.sorted { $0.0 < $1.0 }.map { $0.1 }
}
precondition(ordered == [6, 2, 4])
```

**Observe:** Tagging each child with its input index restores submission order: [6, 2, 4].

Completion order is unspecified, and sorting by value would give [2, 4, 6]; sorting by the carried index reconstructs the order the inputs were submitted.

### Task 3: Independent construction

Implement bounded admission for a small list with at most two outstanding children.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let inputs = [1, 2, 3, 4, 5]
let (results, peak) = await withTaskGroup(
  of: Int.self, returning: ([Int], Int).self
) { group in
  var next = 0
  var outstanding = 0
  var peak = 0
  var collected: [Int] = []
  while next < inputs.count && outstanding < 2 {
    let value = inputs[next]
    group.addTask { value * 10 }
    next += 1
    outstanding += 1
    peak = max(peak, outstanding)
  }
  while let finished = await group.next() {
    collected.append(finished)
    outstanding -= 1
    if next < inputs.count {
      let value = inputs[next]
      group.addTask { value * 10 }
      next += 1
      outstanding += 1
      peak = max(peak, outstanding)
    }
  }
  return (collected.sorted(), peak)
}
precondition(results == [10, 20, 30, 40, 50] && peak == 2)
```

**Observe:** All five inputs are processed, and at most two child tasks were ever outstanding.

A new child is added only after group.next() returns a finished one, so admission is bounded by construction, not by timing.

### Task 4: Diagnose a defect

Diagnose concurrent mutation of a shared result array inside child tasks.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let doubled = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
  for value in [4, 5] { group.addTask { value * 2 } }
  var results: [Int] = []
  for await result in group { results.append(result) }
  return results.sorted()
}
precondition(doubled == [8, 10])
```

**Observe:** Children return their values and the parent alone appends them, giving [8, 10].

Appending to a shared var from inside addTask is rejected in Swift 6 as mutation of a captured var in concurrently-executing code, because two children could write at once. Returning values moves every write to the single owner.

### Task 5: Boundary evidence

Test empty input and a failing child using a throwing group.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
enum ChildError: Error { case failed }
let empty = try await withThrowingTaskGroup(of: Int.self, returning: Int.self) { group in
  var total = 0
  for try await value in group { total += value }
  return total
}
precondition(empty == 0)
var failed = false
do {
  _ = try await withThrowingTaskGroup(of: Int.self, returning: Int.self) { group in
    for value in [1, 2, 3] {
      group.addTask {
        if value == 2 { throw ChildError.failed }
        return value
      }
    }
    var total = 0
    for try await value in group { total += value }
    return total
  }
} catch ChildError.failed {
  failed = true
}
precondition(failed)
```

**Observe:** An empty throwing group returns 0, and the child that throws on 2 makes the whole group throw ChildError.failed.

for try await rethrows the first child error, and leaving the group by throwing cancels and awaits the remaining children, so no partial total escapes.

### Task 6: Transfer and justify

Choose a concurrency bound for an I/O workload and explain its resource basis.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Implement bounded admission for a small list with at most two outstanding children) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A adds three child tasks to a task group, each doubling one input, and the parent collects results with `for await` before sorting. Example B iterates a group with no children. The task 3 answer limits admission so at most two children are outstanding while all five inputs are processed.

**Why it is correct.** Children may finish in any order, so the parent sorts before checking `[2, 4, 6]`. Only the parent appends to `results`, so no shared mutable array crosses task boundaries. An empty group ends its loop immediately and the sum stays 0. In task 3 all five inputs are processed and at most two child tasks were ever outstanding.

**A plausible wrong approach.** Checking `values == [2, 4, 6]` without the `sorted()` call may pass on one run and fail on another, because completion order is unspecified. Declaring `var results` outside and appending inside `addTask` is the task 4 defect; Swift 6 rejects capturing that mutable variable in a concurrently executing closure.

**How to verify.** For task 2, return `(index, value)` pairs from each child and sort by index to reconstruct submission order. Remove `.sorted()` and run several times to see that the check is not guaranteed, then restore it.

## Mechanism and diagnostic reasoning

A task group creates child tasks whose lifetimes remain inside the group scope. Children may finish in any order, so result collection should not accidentally depend on scheduling. If output ordering matters, include an identity or sort after collection. Structured ownership makes it possible to await all admitted work before returning.

A group is not automatically a concurrency limit. Adding a child for every element of a huge input can overwhelm memory or downstream systems. Bound admission by adding only a limited number and replacing completed work. The fixture uses three tiny tasks and explicitly avoids claiming a timing speedup.

withTaskGroup creates a scoped group. addTask admits a child. for await consumes completed child results. A child captures only sendable data crossing the concurrency boundary.

Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.

## Review before continuing

Run the reference and confirm that it prints `swift-029: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
