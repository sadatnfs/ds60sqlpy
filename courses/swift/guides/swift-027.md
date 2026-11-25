# swift-027: Testing behavior with the prepared package

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-026`

## Learning objectives

Write behavior tests for the prepared package with XCTest and know where Swift Testing fits. The central exercise is task 3: Add a real JourneyCore test that rejects a blank item title.

## Purpose and mental model

A meaningful test rejects a plausible wrong implementation. Examples should include independently derived expected values, boundaries and a known misconception. Properties such as idempotence can cover a wider family, but they complement concrete expected cases rather than replacing them.

The pad uses precondition for dependency-free executable checks. The JourneyCore package includes XCTest tests available with the prepared Swift toolchain. Swift Testing (import Testing, @Test, #expect) also ships with Swift 6 toolchains, including the Linux toolchain used here, and swift test runs it alongside XCTest without an extra package dependency. This fixture keeps XCTest so its existing tests stay unchanged. Keep whichever test surface is actually prepared explicit. Unit tests do not prove UI interaction, signing or remote service availability.

## Vocabulary and concepts

**Oracle:** An independent rule deciding correct behavior.

**Regression:** A test retaining evidence of a repaired defect.

**Property:** A relationship expected across a family of inputs.

## How to run this lesson

The pad examples need no fixture, but task 3 adds a test to the copied JourneyCore package and is run with `swift test` there. Task 2 adds `Int.min`, the one value whose negation does not fit in `Int`. Writing `-Int.min` literally is rejected at compile time as an overflow, and negating a variable that holds it traps at runtime, so the clamp must avoid negation entirely.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Run the checked-in package tests using the commands in [JourneyCore](../fixtures/JourneyCore/README.md). Apple UI tests are a separate later lab.

## Syntax anatomy and execution trace

Table-driven checks separate input fixtures from execution. XCTest test methods use XCTAssertEqual and XCTAssertThrowsError in the package. Async tests should await owned work rather than sleep and guess.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** Each tuple in `cases` pairs an input with an expected output written from the rule, not computed by calling the function under test. The loop destructures each pair. For -2 the clamp returns 0, for 0 it returns 0 and for 3 it returns 3, and each result is compared with its literal. The three cases cover a value below the boundary, the boundary itself and a value above it, which is the smallest set that pins this contract.

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

**Trace.** `wrong` returns 1 for any value at or below 0, a plausible slip when someone confuses at least zero with at least one. At input 0 it returns 1 while the clamp returns 0, so the first check proves the fixture can tell them apart. The second check states a property: clamping -4 gives 0, and clamping that 0 again still gives 0. Properties like idempotence add evidence, but only the boundary case catches this particular wrong rule.

## Exercises

1. **Predict and explain.** Name a wrong implementation rejected by each fixture.

2. **Guided modification.** Add the minimum Int case without unsafe negation.

3. **Independent construction.** Add a real JourneyCore test that rejects a blank item title.

4. **Diagnose a defect.** Diagnose a test comparing the same function call on both sides.

5. **Boundary evidence.** Test empty, duplicate and malformed inputs separately.

6. **Transfer and justify.** Create a verification plan distinguishing unit, package, UI and device evidence.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.

Task 4's useless test compares `clamp(x)` with `clamp(x)`. It passes for every implementation, including `wrong`, so it cannot fail and proves nothing. The repair replaces one side with an independently derived literal. Run the suite against a deliberately broken clamp: a meaningful test fails, a tautological one stays green. Keep that broken version in a scratch copy, never in the package.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Check independently derived cases) before changing anything, and confirm its observation: Normal and boundary values satisfy the clamp contract.
2. Compare Example B (Catch a plausible wrong boundary) with Example A and name the first line whose behavior differs. Its observation is: The zero case catches the wrong default and clamping is idempotent.
3. Before opening the explanation, check your task 3 attempt (Add a real JourneyCore test that rejects a blank item title) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

For each of the three fixtures in Example A, name one wrong implementation it rejects that the other two accept. Explain why an expected value should come from the rule rather than from running the code. Separate what a passing `swift test` proves from what still needs UI or device evidence.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The XCTest documentation describes test cases and assertions, and the Swift Package Manager documentation explains test targets and `swift test`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
