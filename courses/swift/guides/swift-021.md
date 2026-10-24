# swift-021: Throwing functions and explicit result values

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-020`

## Learning objectives

Write a throwing validator for an inventory record. Then choose Optional, throws or Result for three APIs and explain each semantic distinction.

## Purpose and mental model

Swift errors represent recoverable failure that a caller must acknowledge with try. A throwing function can return its normal type or throw an Error value. Catching belongs at a layer that can recover, translate or report meaningfully. A generic fallback can hide a failed operation as an ordinary empty result.

Result stores success or failure as a value, useful when an outcome must be retained or passed through another API. Optional absence and errors are different: a missing lookup may be expected, while malformed input carries a reason. Preserve those distinctions instead of force-trying external operations.

## Vocabulary and concepts

**Error:** A value describing recoverable failure.

**Throwing function:** A function that can exit through an error path.

**Result:** A stored success-or-failure value.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`throws` declares failure capability. `try` acknowledges a throwing call. `do/catch` handles errors. Result<Success, Failure> stores an outcome, with Failure conforming to Error.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Validate before returning

Failure carries a domain category instead of masquerading as zero.

```swift
import Foundation

enum QuantityError: Error { case invalid }
func parseQuantity(_ text: String) throws -> Int { guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }; return value }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let parsed = try parseQuantity("3")
            precondition(parsed == 3)
            var rejected = false
            do { _ = try parseQuantity("-1") } catch QuantityError.invalid { rejected = true }
            precondition(rejected)
        }
        print("swift-021: passed")
    }
}
```

**Observe:** Three is accepted and a negative quantity is rejected.

### Example B: Store an outcome for later inspection

Result separates when an operation executes from when its outcome is examined.

```swift
import Foundation

enum QuantityError: Error { case invalid }
func parseQuantity(_ text: String) throws -> Int { guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }; return value }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let outcome = Result { try parseQuantity("bad") }
            switch outcome { case .success: preconditionFailure("invalid input accepted"); case .failure(let error): precondition(error is QuantityError) }
        }
        print("swift-021: passed")
    }
}
```

**Observe:** The stored outcome retains a QuantityError.

## Exercises

1. **Predict and explain.** Trace the normal and throwing paths.

2. **Guided modification.** Distinguish malformed text from negative quantity with separate error cases.

3. **Independent construction.** Write a throwing validator for an inventory record.

4. **Diagnose a defect.** Diagnose try? used where discarding the error reason loses required evidence.

5. **Boundary evidence.** Test empty, zero and out-of-range input.

6. **Transfer and justify.** Choose Optional, throws or Result for three APIs and explain each semantic distinction.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Error, Throwing function, Result without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-021: Throwing functions and explicit result values.
Read courses/swift/guides/swift-021.md and courses/swift/lessons/swift-021.swift. Prerequisites: swift-020.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-021_solution.swift and
courses/swift/solutions/swift-021_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
