# swift-007: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-007_solution.swift](swift-007_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Accumulate a total:** Before each iteration, total summarizes exactly the values already visited. The total is 12 and the empty total is zero.

**Stop at the first match:** The break encodes first-match semantics rather than accidentally returning the last match. The first 8 appears at offset 1 and 9 is absent.

## Task answers

### Task 1: Predict and explain

Write the accumulator trace for every iteration.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Before each iteration, total summarizes exactly the values already visited. The total is 12 and the empty total is zero.

### Task 2: Guided modification

Ignore negative values while preserving a stated invariant.

No separate reference answer has been written for this task. Start from Example B: The break encodes first-match semantics rather than accidentally returning the last match. The first 8 appears at offset 1 and 9 is absent.

### Task 3: Independent construction

Implement a first-match search with an optional result.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func firstIndex(of target: Int, in values: [Int]) -> Int? {
  for (offset, value) in values.enumerated() where value == target {
    return offset
  }
  return nil
}
precondition(firstIndex(of: 7, in: [5, 7, 7]) == 1)
precondition(firstIndex(of: 9, in: [5, 7]) == nil)
precondition(firstIndex(of: 1, in: []) == nil)
```

**Observe:** The first 7 is at offset 1; a missing target and an empty array give nil.

The loop returns at the first match, and nil keeps not-found separate from every valid offset.

### Task 4: Diagnose a defect

Diagnose a while loop whose progress variable never changes.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.

### Task 5: Boundary evidence

Test empty, singleton and repeated-match inputs.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Accumulate a total) and Example B (Stop at the first match).

### Task 6: Transfer and justify

Design a bounded retry loop and explain both its invariant and its stop condition.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Invariant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A loop repeats a state transformation. Its invariant explains what remains true before and after every iteration. A termination argument explains why the loop eventually stops. These two ideas make a loop easier to reason about than simply reading each statement repeatedly.

For-in traversal expresses iteration over a sequence. Use enumerated when the traversal offset is useful, but do not assume that an enumerated offset is a valid index for every collection or slice. Arrays use integer indices; other collections may not. Empty input should leave the initial accumulator in a meaningful state.

`for value in values` traverses elements. `for (offset, value) in values.enumerated()` adds a traversal counter. `break` stops the loop; `continue` skips the remaining body. A while loop needs an explicit progress step.

An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.

## Review before continuing

Run the reference and confirm that it prints `swift-007: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
