# swift-014: Properties, observers and derived state

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-013`

## Learning objectives

Build a value model with one stored unit and a documented converted view. Then choose an explicit method instead of a setter for a state change with validation and failure.

## Purpose and mental model

A stored property retains data; a computed property derives a value from other state. Prefer deriving cheap dependent values instead of storing duplicates that can disagree. A property observer reacts to a stored-value change but should not become an invisible substitute for a clear domain operation.

Computed setters translate an external representation back into stored state. That translation may lose information, so document it. Access control can permit reading without external writing. Property wrappers later package reusable access behavior, but start by understanding the plain getter and setter contract.

## Vocabulary and concepts

**Stored property:** A field retaining state.

**Computed property:** A value derived on access.

**Observer:** Code invoked around a stored-property change.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`var area: Int { width * height }` computes a value. `get` and `set` define two-way access; newValue names the assigned value. didSet observes assignments after the new value is stored.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Derive instead of duplicating

One source of truth prevents stale duplicated state.

```swift
import Foundation

struct Rectangle {
  var width: Int
  var height: Int
  var area: Int { width * height }
}
struct Temperature {
  var celsius: Double
  var fahrenheit: Double {
    get { celsius * 9 / 5 + 32 }
    set { celsius = (newValue - 32) * 5 / 9 }
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var rectangle = Rectangle(width: 3, height: 4)
      precondition(rectangle.area == 12)
      rectangle.width = 5
      precondition(rectangle.area == 20)
    }
    print("swift-014: passed")
  }
}
```

**Observe:** Area changes with width without a separately updated area field.

### Example B: Expose a conversion property

A computed property can expose a convenient representation while retaining one stored unit.

```swift
import Foundation

struct Rectangle {
  var width: Int
  var height: Int
  var area: Int { width * height }
}
struct Temperature {
  var celsius: Double
  var fahrenheit: Double {
    get { celsius * 9 / 5 + 32 }
    set { celsius = (newValue - 32) * 5 / 9 }
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var temperature = Temperature(celsius: 0)
      precondition(temperature.fahrenheit == 32)
      temperature.fahrenheit = 212
      precondition(abs(temperature.celsius - 100) < 1e-9)
    }
    print("swift-014: passed")
  }
}
```

**Observe:** The getter and setter translate between temperature scales.

## Exercises

1. **Predict and explain.** Trace which properties are stored and which are derived.

2. **Guided modification.** Add a computed rectangle perimeter.

3. **Independent construction.** Build a value model with one stored unit and a documented converted view.

4. **Diagnose a defect.** Diagnose a separately stored area that is not updated after width changes.

5. **Boundary evidence.** Test zero and a non-integer conversion case.

6. **Transfer and justify.** Choose an explicit method instead of a setter for a state change with validation and failure.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Stored property, Computed property, Observer without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-014: Properties, observers and derived state.
Read courses/swift/guides/swift-014.md and courses/swift/lessons/swift-014.swift. Prerequisites: swift-013.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-014_solution.swift and
courses/swift/solutions/swift-014_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
