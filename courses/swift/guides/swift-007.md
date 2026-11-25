# swift-007: Loops, invariants and safe traversal

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-006`

## Learning objectives

Write loops with safe traversal and report not-found with an optional result. The central exercise is task 3: Implement a first-match search with an optional result.

## Purpose and mental model

A loop repeats a state transformation. Its invariant explains what remains true before and after every iteration. A termination argument explains why the loop eventually stops. These two ideas make a loop easier to reason about than simply reading each statement repeatedly.

For-in traversal expresses iteration over a sequence. Use enumerated when the traversal offset is useful, but do not assume that an enumerated offset is a valid index for every collection or slice. Arrays use integer indices; other collections may not. Empty input should leave the initial accumulator in a meaningful state.

## Vocabulary and concepts

**Invariant:** A property preserved by every iteration.

**Accumulator:** State summarizing processed input.

**Termination argument:** A reason the loop cannot continue indefinitely.

## How to run this lesson

Task 1 wants the accumulator written out for every iteration, so keep a paper table beside Example A while it runs. Task 4 studies a loop whose progress variable never changes; run that experiment with an explicit iteration cap in the condition rather than waiting on a program that never reaches its marker.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`for value in values` traverses elements. `for (offset, value) in values.enumerated()` adds a traversal counter. `break` stops the loop; `continue` skips the remaining body. A while loop needs an explicit progress step.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Accumulate a total

Before each iteration, total summarizes exactly the values already visited.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 4, 6]
      var total = 0
      for value in values { total += value }
      precondition(total == 12)
      precondition([Int]().reduce(0, +) == 0)
    }
    print("swift-007: passed")
  }
}
```

**Observe:** The total is 12 and the empty total is zero.

**Trace.** Before the loop, `total` is 0 and nothing has been visited. The first iteration reads 2 and stores 2; the second reads 4 and stores 6; the third reads 6 and stores 12. At the start of every iteration the invariant holds: `total` equals the sum of the elements already seen. The second check covers the empty array, where `reduce(0, +)` returns its starting value 0 without calling `+` at all. An empty input is the case most likely to expose an accumulator seeded with the first element.

### Example B: Stop at the first match

The break encodes first-match semantics rather than accidentally returning the last match.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [3, 8, 8]
      var found: Int? = nil
      for (offset, value) in values.enumerated() {
        if value == 8 {
          found = offset
          break
        }
      }
      precondition(found == 1)
      precondition(values.firstIndex(of: 9) == nil)
    }
    print("swift-007: passed")
  }
}
```

**Observe:** The first 8 appears at offset 1 and 9 is absent.

**Trace.** `found` starts as nil. At offset 0 the value is 3, so the body does nothing. At offset 1 the value is 8; `found` becomes 1 and `break` leaves the loop at once, so offset 2, which also holds 8, is never examined. Without the `break`, the loop would overwrite `found` with 2 and report the last match. The final check uses `firstIndex(of:)`, which already implements first-match search, to show that an absent value yields nil rather than a sentinel such as -1.

## Exercises

1. **Predict and explain.** Write the accumulator trace for every iteration.

2. **Guided modification.** Ignore negative values while preserving a stated invariant.

3. **Independent construction.** Implement a first-match search with an optional result.

4. **Diagnose a defect.** Diagnose a while loop whose progress variable never changes.

5. **Boundary evidence.** Test empty, singleton and repeated-match inputs.

6. **Transfer and justify.** Design a bounded retry loop and explain both its invariant and its stop condition.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.

A first-match search that forgets `break` passes on any input with a single match, which makes the bug easy to miss. The counterexample is a repeated-match input such as `[5, 7, 7]` searched for 7: the correct offset is 1 and the buggy one is 2. Add the empty array and a singleton as well; neither may touch an index outside the array.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Accumulate a total) before changing anything, and confirm its observation: The total is 12 and the empty total is zero.
2. Compare Example B (Stop at the first match) with Example A and name the first line whose behavior differs. Its observation is: The first 8 appears at offset 1 and 9 is absent.
3. Before opening the explanation, check your task 3 attempt (Implement a first-match search with an optional result) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Describe the invariant of Example A in one sentence that stays true at the start of any iteration. Explain why the offset from `enumerated()` equals the index for an `Array` but not for an `ArraySlice`. Write the stop condition of a bounded retry loop and name the value that changes on every pass.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): See the Control Flow chapter of the Swift book for for-in loops, while loops and control transfer statements such as break and continue.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-007: Loops, invariants and safe traversal.
Read courses/swift/guides/swift-007.md and courses/swift/lessons/swift-007.swift. Prerequisites: swift-006.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-007_solution.swift and
courses/swift/solutions/swift-007_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
