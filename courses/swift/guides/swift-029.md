# swift-029: Task groups and bounded parallel ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-028`

## Learning objectives

Run bounded parallel work with task groups that own their child tasks. The central exercise is task 3: Implement bounded admission for a small list with at most two outstanding children.

## Purpose and mental model

A task group creates child tasks whose lifetimes remain inside the group scope. Children may finish in any order, so result collection should not accidentally depend on scheduling. If output ordering matters, include an identity or sort after collection. Structured ownership makes it possible to await all admitted work before returning.

A group is not automatically a concurrency limit. Adding a child for every element of a huge input can overwhelm memory or downstream systems. Bound admission by adding only a limited number and replacing completed work. The fixture uses three tiny tasks and explicitly avoids claiming a timing speedup.

## Vocabulary and concepts

**Child task:** Work owned by a structured parent scope.

**Completion order:** The order tasks finish, potentially different from submission.

**Admission limit:** A bound on simultaneously outstanding work.

## How to run this lesson

Task groups produce results in completion order, which varies between runs. Run Example A several times and print the unsorted results in a scratch pad if you want to see the variation, but keep the sorted comparison in the check. Task 4's shared-array mutation is rejected at compile time under Swift 6 checking rather than producing a wrong answer at runtime.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

withTaskGroup creates a scoped group. addTask admits a child. for await consumes completed child results. A child captures only sendable data crossing the concurrency boundary.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Collect results without assuming order

Independent values cross the boundary, and the parent alone mutates the result array.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
        for value in [1, 2, 3] { group.addTask { value * 2 } }
        var results: [Int] = []
        for await result in group { results.append(result) }
        return results.sorted()
      }
      precondition(values == [2, 4, 6])
    }
    print("swift-029: passed")
  }
}
```

**Observe:** Sorted results are deterministic despite unspecified completion order.

**Trace.** `withTaskGroup` creates a group whose children each return an `Int`. The loop adds three children, each capturing its own immutable `value` and returning it doubled. The parent then iterates `for await result in group`, receiving 2, 4 and 6 in whatever order the children finish, and appends each to its local `results` array. Only the parent touches that array. After the group is exhausted, `sorted()` gives `[2, 4, 6]` regardless of completion order.

### Example B: Handle an empty group

The empty path needs no special background work or timer.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let count = await withTaskGroup(of: Int.self, returning: Int.self) { group in
        var total = 0
        for await value in group { total += value }
        return total
      }
      precondition(count == 0)
    }
    print("swift-029: passed")
  }
}
```

**Observe:** No admitted children produces the identity result zero.

**Trace.** This group receives no children at all. The `for await` loop asks the group for its next result, the group reports that it has no pending children, and the loop ends without running its body. `total` stays at its initial 0 and the closure returns it. The empty case needs no timeout or special flag: an empty group completes as soon as it is iterated, and 0 is the natural identity for a sum.

## Exercises

1. **Predict and explain.** Identify who owns each task and the result array.

2. **Guided modification.** Attach input indices and reconstruct submission ordering.

3. **Independent construction.** Implement bounded admission for a small list with at most two outstanding children.

4. **Diagnose a defect.** Diagnose concurrent mutation of a shared result array inside child tasks.

5. **Boundary evidence.** Test empty input and a failing child using a throwing group.

6. **Transfer and justify.** Choose a concurrency bound for an I/O workload and explain its resource basis.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.

Task 4's version appends to a shared `var results` from inside each child closure. Swift 6 rejects it at compile time with a data-race diagnostic about the child closure; the exact wording varies between toolchain releases, so record the message you get as evidence. For task 2, tag each child result with its input index and rebuild the original order; the check must pass whatever order the children complete in.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Collect results without assuming order) before changing anything, and confirm its observation: Sorted results are deterministic despite unspecified completion order.
2. Compare Example B (Handle an empty group) with Example A and name the first line whose behavior differs. Its observation is: No admitted children produces the identity result zero.
3. Before opening the explanation, check your task 3 attempt (Implement bounded admission for a small list with at most two outstanding children) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain who owns the result array and why no child may modify it. Describe what `for await` does when the group has no pending children. For task 3, explain how waiting for one child before adding the next keeps at most two outstanding, and what resource such a bound protects in an I/O workload.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Task groups and structured concurrency get their own section of the book's Concurrency chapter; the standard library documents `withTaskGroup(of:returning:body:)`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-029: Task groups and bounded parallel ownership.
Read courses/swift/guides/swift-029.md and courses/swift/lessons/swift-029.swift. Prerequisites: swift-028.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-029_solution.swift and
courses/swift/solutions/swift-029_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
