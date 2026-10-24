# swift-027: Testing behavior with the prepared package

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-026`

## Learning objectives

Add a real JourneyCore test for rejected negative quantity. Then create a verification plan distinguishing unit, package, UI and device evidence.

## Purpose and mental model

A meaningful test rejects a plausible wrong implementation. Examples should include independently derived expected values, boundaries and a known misconception. Properties such as idempotence can cover a wider family, but they complement concrete expected cases rather than replacing them.

The pad uses precondition for dependency-free executable checks. The JourneyCore package includes XCTest tests available with the prepared Swift toolchain. Swift Testing is another modern test framework and its macro-based API has a distinct project/toolchain requirement. Keep whichever test surface is actually prepared explicit. Unit tests do not prove UI interaction, signing or remote service availability.

## Vocabulary and concepts

**Oracle:** An independent rule deciding correct behavior.

**Regression:** A test retaining evidence of a repaired defect.

**Property:** A relationship expected across a family of inputs.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Run the checked-in package tests using the commands in [JourneyCore](../fixtures/JourneyCore/README.md). Apple UI tests are a separate later lab.

## Syntax anatomy and execution trace

Table-driven checks separate input fixtures from execution. XCTest test methods use XCTAssertEqual and XCTAssertThrowsError in the package. Async tests should await owned work rather than sleep and guess.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Check independently derived cases

Literal expected results are derived from the domain rule rather than a duplicated implementation.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let cases = [(-2, 0), (0, 0), (3, 3)]
            for (input, expected) in cases { precondition(max(0, input) == expected) }
        }
        print("swift-027: passed")
    }
}
```

**Observe:** Normal and boundary values satisfy the clamp contract.

### Example B: Catch a plausible wrong boundary

A property adds evidence while the boundary example remains decisive.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            func wrong(_ value: Int) -> Int { value <= 0 ? 1 : value }
            precondition(wrong(0) != max(0, 0))
            precondition(max(0, max(0, -4)) == max(0, -4))
        }
        print("swift-027: passed")
    }
}
```

**Observe:** The zero case catches the wrong default and clamping is idempotent.

## Exercises

1. **Predict and explain.** Name a wrong implementation rejected by each fixture.

2. **Guided modification.** Add the minimum Int case without unsafe negation.

3. **Independent construction.** Add a real JourneyCore test for rejected negative quantity.

4. **Diagnose a defect.** Diagnose a test comparing the same function call on both sides.

5. **Boundary evidence.** Test empty, duplicate and malformed inputs separately.

6. **Transfer and justify.** Create a verification plan distinguishing unit, package, UI and device evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Oracle, Regression, Property without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-027: Testing behavior with the prepared package.
Read courses/swift/guides/swift-027.md and courses/swift/lessons/swift-027.swift. Prerequisites: swift-026.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-027_solution.swift and
courses/swift/solutions/swift-027_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
