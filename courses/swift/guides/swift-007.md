# swift-007: Loops, invariants and safe traversal

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-006`

## Learning objectives

Implement a first-match search with an optional result. Then design a bounded retry loop and explain both its invariant and its stop condition.

## Purpose and mental model

A loop repeats a state transformation. Its invariant explains what remains true before and after every iteration. A termination argument explains why the loop eventually stops. These two ideas make a loop easier to reason about than simply reading each statement repeatedly.

For-in traversal expresses iteration over a sequence. Use enumerated when the traversal offset is useful, but do not assume that an enumerated offset is a valid index for every collection or slice. Arrays use integer indices; other collections may not. Empty input should leave the initial accumulator in a meaningful state.

## Vocabulary and concepts

**Invariant:** A property preserved by every iteration.

**Accumulator:** State summarizing processed input.

**Termination argument:** A reason the loop cannot continue indefinitely.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`for value in values` traverses elements. `for (offset, value) in values.enumerated()` adds a traversal counter. `break` stops the loop; `continue` skips the remaining body. A while loop needs an explicit progress step.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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
            for (offset, value) in values.enumerated() { if value == 8 { found = offset; break } }
            precondition(found == 1)
            precondition(values.firstIndex(of: 9) == nil)
        }
        print("swift-007: passed")
    }
}
```

**Observe:** The first 8 appears at offset 1 and 9 is absent.

## Exercises

1. **Predict and explain.** Write the accumulator trace for every iteration.

2. **Guided modification.** Ignore negative values while preserving a stated invariant.

3. **Independent construction.** Implement a first-match search with an optional result.

4. **Diagnose a defect.** Diagnose a while loop whose progress variable never changes.

5. **Boundary evidence.** Test empty, singleton and repeated-match inputs.

6. **Transfer and justify.** Design a bounded retry loop and explain both its invariant and its stop condition.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Invariant, Accumulator, Termination argument without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
