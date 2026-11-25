# swift-007: explanation and comparison

Reference program: [swift-007_solution.swift](swift-007_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Accumulate a total:** Before each iteration, total summarizes exactly the values already visited. The total is 12 and the empty total is zero.

**Stop at the first match:** The break encodes first-match semantics rather than accidentally returning the last match. The first 8 appears at offset 1 and 9 is absent.

## Task answers

### Task 1: Predict and explain

Write the accumulator trace for every iteration.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let values = [2, 4, 6]
var total = 0
var trace: [Int] = []
for value in values {
  total += value
  trace.append(total)
}
precondition(trace == [2, 6, 12] && total == 12)
```

**Observe:** The accumulator is 2, then 6, then 12 after the three iterations.

Each iteration adds one element to the running total, so after k iterations total equals the sum of the first k values; the recorded trace shows that invariant step by step.

### Task 2: Guided modification

Ignore negative values while preserving a stated invariant.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let values = [2, -3, 4]
var total = 0
var kept: [Int] = []
for value in values where value >= 0 {
  total += value
  kept.append(value)
  precondition(total == kept.reduce(0, +))
}
precondition(total == 6 && kept == [2, 4])
```

**Observe:** -3 is skipped, so the total is 6 from the kept values 2 and 4.

The invariant changes to: total equals the sum of the nonnegative values seen so far. The where clause skips negatives, and the in-loop precondition checks the invariant on every iteration.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let values = [3, 8, 8]
var index = 0
var steps = 0
while index < values.count && values[index] != 8 {
  index += 1
  steps += 1
}
precondition(index == 1 && steps == 1)
```

**Observe:** The loop stops at index 1 after one step.

Without index += 1 the condition values[0] != 8 stays true forever. The progress variable must change in the body, and each step must move it toward the bound values.count.

### Task 5: Boundary evidence

Test empty, singleton and repeated-match inputs.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func firstOffset(of target: Int, in values: [Int]) -> Int? {
  for (offset, value) in values.enumerated() where value == target {
    return offset
  }
  return nil
}
precondition(firstOffset(of: 4, in: []) == nil)
precondition(firstOffset(of: 4, in: [4]) == 0 && firstOffset(of: 9, in: [4]) == nil)
precondition(firstOffset(of: 4, in: [1, 4, 4, 4]) == 1)
```

**Observe:** The empty array gives nil, the singleton gives 0 or nil, and repeated matches report the first offset 1.

The loop returns at the first match, so later duplicates are never visited; an empty input never enters the loop and falls through to nil.

### Task 6: Transfer and justify

Design a bounded retry loop and explain both its invariant and its stop condition.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A sums `[2, 4, 6]` with a `for` loop and a `var total`, then checks the empty-array reduction separately. Example B walks `[3, 8, 8]` with `enumerated()` and breaks on the first 8. The task 3 answer returns the offset of the first match as an `Int?`, so absence has its own value.

**Why it is correct.** Before each pass, `total` equals the sum of the elements already visited: 0, then 2, then 6, then 12. The invariant holds for an empty array too, giving 0. In Example B the `break` stops at offset 1, so the duplicate 8 at offset 2 never overwrites `found`. `firstIndex(of: 9)` is nil because 9 never appears.

**A plausible wrong approach.** Removing the `break` still compiles, but the loop then records offset 2, the last 8, and `found == 1` fails. Returning -1 for not found is another trap: a later `values[-1]` traps at runtime. A `while` loop whose index is never incremented never terminates, which task 4 asks you to diagnose.

**How to verify.** For task 3, the first 7 is at offset 1, and both a missing target and an empty array give nil. Write the four-row accumulator trace for `[2, 4, 6]` (0, 2, 6, 12) and compare it with a `print(total)` placed temporarily inside the loop.

## Mechanism and diagnostic reasoning

A loop repeats a state transformation. Its invariant explains what remains true before and after every iteration. A termination argument explains why the loop eventually stops. These two ideas make a loop easier to reason about than simply reading each statement repeatedly.

For-in traversal expresses iteration over a sequence. Use enumerated when the traversal offset is useful, but do not assume that an enumerated offset is a valid index for every collection or slice. Arrays use integer indices; other collections may not. Empty input should leave the initial accumulator in a meaningful state.

`for value in values` traverses elements. `for (offset, value) in values.enumerated()` adds a traversal counter. `break` stops the loop; `continue` skips the remaining body. A while loop needs an explicit progress step.

An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.

## Review before continuing

Run the reference and confirm it prints `swift-007: passed`, then rerun the guide's counterexample.
