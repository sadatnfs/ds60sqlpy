# swift-003: Numeric limits and intentional arithmetic

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-002`

## Learning objectives

Write checked quantity addition that returns an explicit rejected outcome. Then choose a numeric representation and rounding policy for a price calculation.

## Purpose and mental model

Integer values have bounded ranges. Ordinary overflowing integer arithmetic traps in Swift, while reporting-overflow operations return both a result and an overflow flag. Wrapping operators are explicit and useful for domains such as fixed-width bit arithmetic, but usually wrong for quantities or balances.

Floating-point values approximate many decimal fractions. Compare a result according to a numerical error contract rather than expecting every decimal identity to hold exactly. Decimal can represent base-ten financial quantities more naturally, but rounding and units still require a policy. A type choice does not replace domain reasoning.

## Vocabulary and concepts

**Overflow:** A result outside the representable range.

**Tolerance:** An allowed numerical error under a stated scale.

**Wrapping arithmetic:** Arithmetic modulo the fixed-width representation.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`addingReportingOverflow` returns a tuple with partialValue and overflow. `&+` explicitly wraps. `abs(actual - expected) < tolerance` expresses a simple absolute error bound appropriate only to the stated scale.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Observe overflow without crashing

The flag is essential: the partial result alone cannot identify the intended mathematical sum.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = UInt8.max.addingReportingOverflow(1)
      precondition(result.overflow)
      precondition(result.partialValue == 0)
      precondition(UInt8(2).addingReportingOverflow(3).partialValue == 5)
    }
    print("swift-003: passed")
  }
}
```

**Observe:** 255 plus one reports overflow and a wrapped partial result of zero.

### Example B: Use a numerical comparison policy

The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let actual = 0.1 + 0.2
      precondition(abs(actual - 0.3) < 1e-12)
      let exact = Decimal(string: "0.1")! + Decimal(string: "0.2")!
      precondition(exact == Decimal(string: "0.3")!)
    }
    print("swift-003: passed")
  }
}
```

**Observe:** The floating result meets the stated tolerance and the decimal fixture retains decimal intent.

## Exercises

1. **Predict and explain.** Predict the overflow flag and partial result.

2. **Guided modification.** Repeat the boundary with UInt8 zero minus one using the reporting operation.

3. **Independent construction.** Write checked quantity addition that returns an explicit rejected outcome.

4. **Diagnose a defect.** Diagnose ignoring the overflow flag.

5. **Boundary evidence.** Compare zero, normal and maximum-range inputs.

6. **Transfer and justify.** Choose a numeric representation and rounding policy for a price calculation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Overflow, Tolerance, Wrapping arithmetic without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-003: Numeric limits and intentional arithmetic.
Read courses/swift/guides/swift-003.md and courses/swift/lessons/swift-003.swift. Prerequisites: swift-002.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-003_solution.swift and
courses/swift/solutions/swift-003_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
