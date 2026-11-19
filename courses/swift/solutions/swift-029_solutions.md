# swift-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-029_solution.swift](swift-029_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Collect results without assuming order:** Independent values cross the boundary, and the parent alone mutates the result array. Sorted results are deterministic despite unspecified completion order.

**Handle an empty group:** The empty path needs no special background work or timer. No admitted children produces the identity result zero.

## Task answers

### Task 1: Predict and explain

Identify who owns each task and the result array.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Independent values cross the boundary, and the parent alone mutates the result array. Sorted results are deterministic despite unspecified completion order.

### Task 2: Guided modification

Attach input indices and reconstruct submission ordering.

No separate reference answer has been written for this task. Start from Example B: The empty path needs no special background work or timer. No admitted children produces the identity result zero.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.

### Task 5: Boundary evidence

Test empty input and a failing child using a throwing group.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Collect results without assuming order) and Example B (Handle an empty group).

### Task 6: Transfer and justify

Choose a concurrency bound for an I/O workload and explain its resource basis.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Child task**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A task group creates child tasks whose lifetimes remain inside the group scope. Children may finish in any order, so result collection should not accidentally depend on scheduling. If output ordering matters, include an identity or sort after collection. Structured ownership makes it possible to await all admitted work before returning.

A group is not automatically a concurrency limit. Adding a child for every element of a huge input can overwhelm memory or downstream systems. Bound admission by adding only a limited number and replacing completed work. The fixture uses three tiny tasks and explicitly avoids claiming a timing speedup.

withTaskGroup creates a scoped group. addTask admits a child. for await consumes completed child results. A child captures only sendable data crossing the concurrency boundary.

Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.

## Review before continuing

Run the reference and confirm that it prints `swift-029: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
