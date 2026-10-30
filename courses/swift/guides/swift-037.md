# swift-037: Property wrappers and reusable access policy

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-036`

## Learning objectives

Create a wrapper with an explicit normalization policy for a local display field. Then choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.

## Purpose and mental model

A property wrapper packages behavior around property storage and access. It can validate, normalize or project a reusable policy, but it should not hide surprising I/O or authorization. The wrappedValue is the property-facing interface; projectedValue can expose related information using dollar-prefixed access.

Wrapper behavior is part of the containing type's semantics. Decide whether invalid assignments are rejected, clamped or represented as an error, and make that choice visible to readers. A clamped value can be appropriate for a display control but inappropriate for financial input where silent correction hides an error.

## Vocabulary and concepts

**Property wrapper:** Reusable logic around a property access contract.

**Wrapped value:** The value exposed through the decorated property.

**Projection:** Additional wrapper-related information exposed separately.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`@propertyWrapper` marks a wrapper type. wrappedValue supplies get/set behavior. `@Clamped var level` applies it. A projectedValue is read through `$level` when declared.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Apply a bounded display policy

The wrapper enforces a deliberate display range at every assignment.

```swift
import Foundation

@propertyWrapper struct Clamped {
  private var value: Int
  let range: ClosedRange<Int>
  init(wrappedValue: Int, _ range: ClosedRange<Int>) {
    self.range = range
    self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
  }
  var wrappedValue: Int {
    get { value }
    set { value = min(max(newValue, range.lowerBound), range.upperBound) }
  }
  var projectedValue: ClosedRange<Int> { range }
}
struct Control { @Clamped(0...10) var level = 0 }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var control = Control()
      control.level = 12
      precondition(control.level == 10)
      control.level = -2
      precondition(control.level == 0)
    }
    print("swift-037: passed")
  }
}
```

**Observe:** Assignments are clamped into zero through ten.

### Example B: Retain valid interior values

The projected information explains the policy without exposing mutable internal storage.

```swift
import Foundation

@propertyWrapper struct Clamped {
  private var value: Int
  let range: ClosedRange<Int>
  init(wrappedValue: Int, _ range: ClosedRange<Int>) {
    self.range = range
    self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
  }
  var wrappedValue: Int {
    get { value }
    set { value = min(max(newValue, range.lowerBound), range.upperBound) }
  }
  var projectedValue: ClosedRange<Int> { range }
}
struct Control { @Clamped(0...10) var level = 0 }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var control = Control()
      control.level = 4
      precondition(control.level == 4)
      precondition(control.$level == 0...10)
    }
    print("swift-037: passed")
  }
}
```

**Observe:** A valid interior value is unchanged and the projection exposes the range.

## Exercises

1. **Predict and explain.** Trace initialization and both setter calls.

2. **Guided modification.** Change the allowed range and update boundary tests.

3. **Independent construction.** Create a wrapper with an explicit normalization policy for a local display field.

4. **Diagnose a defect.** Explain why silently clamping a payment amount would be misleading.

5. **Boundary evidence.** Test both endpoints and one value outside each.

6. **Transfer and justify.** Choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Property wrapper, Wrapped value, Projection without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-037: Property wrappers and reusable access policy.
Read courses/swift/guides/swift-037.md and courses/swift/lessons/swift-037.swift. Prerequisites: swift-036.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-037_solution.swift and
courses/swift/solutions/swift-037_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
