# swift-029: Task groups and bounded parallel ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-028`

## Learning objectives

Implement bounded admission for a small list with at most two outstanding children. Then choose a concurrency bound for an I/O workload and explain its resource basis.

## Purpose and mental model

A task group creates child tasks whose lifetimes remain inside the group scope. Children may finish in any order, so result collection should not accidentally depend on scheduling. If output ordering matters, include an identity or sort after collection. Structured ownership makes it possible to await all admitted work before returning.

A group is not automatically a concurrency limit. Adding a child for every element of a huge input can overwhelm memory or downstream systems. Bound admission by adding only a limited number and replacing completed work. The fixture uses three tiny tasks and explicitly avoids claiming a timing speedup.

## Vocabulary and concepts

**Child task:** Work owned by a structured parent scope.

**Completion order:** The order tasks finish, potentially different from submission.

**Admission limit:** A bound on simultaneously outstanding work.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

withTaskGroup creates a scoped group. addTask admits a child. for await consumes completed child results. A child captures only sendable data crossing the concurrency boundary.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Identify who owns each task and the result array.

2. **Guided modification.** Attach input indices and reconstruct submission ordering.

3. **Independent construction.** Implement bounded admission for a small list with at most two outstanding children.

4. **Diagnose a defect.** Diagnose concurrent mutation of a shared result array inside child tasks.

5. **Boundary evidence.** Test empty input and a failing child using a throwing group.

6. **Transfer and justify.** Choose a concurrency bound for an I/O workload and explain its resource basis.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Child task, Completion order, Admission limit without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
