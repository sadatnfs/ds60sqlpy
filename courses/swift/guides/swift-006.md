# swift-006: Branches, switch and exhaustive reasoning

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-005`

## Learning objectives

Write a three-way classifier for negative, zero and positive quantities. Then replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.

## Purpose and mental model

Control flow selects which operations execute. A branch should correspond to a domain distinction that can be explained before reading the code. Swift switch does not implicitly fall through to the next case, and the compiler requires coverage of possible inputs. This helps make state handling deliberate.

Range boundaries remain a source of mistakes. A closed range includes both ends; a half-open range excludes its upper end. Use fixtures exactly at transitions and outside the valid domain. A broad default can satisfy exhaustiveness while still hiding a new state, so prefer explicit enum cases when the domain is finite.

## Vocabulary and concepts

**Exhaustiveness:** Handling every possible input category.

**Closed range:** A range including both endpoints.

**Half-open range:** A range excluding its upper endpoint.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`if` requires a Bool. `switch` matches cases without implicit fallthrough. `0..<10` excludes ten; `0...10` includes it. A where clause narrows a matched case.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Classify thresholds

The ranges express the inclusive boundary and keep out-of-domain values separate.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            func classify(_ score: Int) -> String { switch score { case 0..<60: return "retry"; case 60...100: return "pass"; default: return "invalid" } }
            precondition(classify(59) == "retry")
            precondition(classify(60) == "pass" && classify(101) == "invalid")
        }
        print("swift-006: passed")
    }
}
```

**Observe:** 59 retries, 60 passes and 101 is invalid.

### Example B: Use a guard for a required value

The unwrapped binding is available after the guard because every failing path has returned.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            func describe(_ text: String?) -> String { guard let text, !text.isEmpty else { return "missing" }; return "value:\(text)" }
            precondition(describe(nil) == "missing")
            precondition(describe("") == "missing" && describe("x") == "value:x")
        }
        print("swift-006: passed")
    }
}
```

**Observe:** The early exit excludes missing and empty values before the valid path.

## Exercises

1. **Predict and explain.** Predict each threshold case before running.

2. **Guided modification.** Move the pass boundary to 70 and update adjacent tests.

3. **Independent construction.** Write a three-way classifier for negative, zero and positive quantities.

4. **Diagnose a defect.** Diagnose a closed range used where an exclusive upper bound was intended.

5. **Boundary evidence.** Test both ends of the valid domain and one value beyond each.

6. **Transfer and justify.** Replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Exhaustiveness, Closed range, Half-open range without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-006: Branches, switch and exhaustive reasoning.
Read courses/swift/guides/swift-006.md and courses/swift/lessons/swift-006.swift. Prerequisites: swift-005.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-006_solution.swift and
courses/swift/solutions/swift-006_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
