# swift-020: Collection protocols, laziness and algorithm costs

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-019`

## Learning objectives

Write a generic sum over Sequence where the element type is suitable. Then choose lazy or materialized processing for a large input and explain repeatability and memory costs.

## Purpose and mental model

Sequence promises iteration but not necessarily repeatability or efficient indexing. Collection adds reusable traversal with indices, and more specialized protocols add bidirectional or random access. Write an algorithm against the capability it needs rather than assuming every sequence behaves like an array.

Lazy transformations defer work until consumption. This can avoid intermediate storage, but it also delays side effects and errors. Keep transformation closures pure. A slice can retain original indices, so using zero-based offsets indiscriminately breaks otherwise generic code. Complexity belongs to the chosen collection and operation, not merely to its spelling.

## Vocabulary and concepts

**Sequence:** A source that can be iterated.

**Collection:** A sequence with reusable traversal and indices.

**Materialization:** Creating stored elements from a sequence.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`collection.indices` supplies valid positions. `lazy.map` creates deferred transformation. `Array(sequence)` materializes. reduce summarizes a sequence without requiring indexing.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use slice indices honestly

Element count and index origin are different properties.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      precondition(slice.startIndex == 1)
      precondition(slice.map { $0 / 10 } == [2, 3])
    }
    print("swift-020: passed")
  }
}
```

**Observe:** The slice starts at index 1 while traversal still produces two elements.

### Example B: Materialize a lazy transformation

Pure transformations keep delayed execution understandable and reproducible.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let transformed = [1, 2, 3].lazy.filter { $0 > 1 }.map { $0 * 10 }
      precondition(Array(transformed) == [20, 30])
      precondition([Int]().reduce(0, +) == 0)
    }
    print("swift-020: passed")
  }
}
```

**Observe:** The lazy recipe produces 20 and 30 when consumed.

## Exercises

1. **Predict and explain.** Predict slice count and startIndex separately.

2. **Guided modification.** Traverse the slice using its indices.

3. **Independent construction.** Write a generic sum over Sequence where the element type is suitable.

4. **Diagnose a defect.** Diagnose indexing a slice from zero to count minus one.

5. **Boundary evidence.** Test an empty slice and a single-pass custom sequence.

6. **Transfer and justify.** Choose lazy or materialized processing for a large input and explain repeatability and memory costs.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Sequence, Collection, Materialization without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-020: Collection protocols, laziness and algorithm costs.
Read courses/swift/guides/swift-020.md and courses/swift/lessons/swift-020.swift. Prerequisites: swift-019.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-020_solution.swift and
courses/swift/solutions/swift-020_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
