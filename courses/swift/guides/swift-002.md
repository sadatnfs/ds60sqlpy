# swift-002: Constants, variables and static types

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-001`

## Learning objectives

Compute a mean from an integer total and count using a deliberate conversion. Then choose units and types for a small measurement model.

## Purpose and mental model

Swift distinguishes a binding that may change from one that may not. `let` prevents reassignment; `var` permits it. Prefer let until a state transition is part of the design. The compiler infers types from context, but inference does not make values dynamically typed. A variable initialized with an Int cannot later become a String.

Conversions are explicit between many numeric types. This makes information-changing boundaries visible. A value being representable in one type does not prove it is valid for a domain. Keep units in names and validation at input boundaries. Later chapters introduce reference types, where a constant reference can still point to a mutable object.

## Vocabulary and concepts

**Binding:** A name associated with a value or reference.

**Type inference:** Compiler deduction of a static type from context.

**Conversion:** An explicit change of representation.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`let count: Int = 3` gives an explicit type. `var total = 0` infers Int. `Double(count)` converts a numeric value. Swift source normally does not need semicolons at line ends.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Reassign only mutable state

The code exposes which part is state and which part is a stable input.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let perBox = 4
      var total = 0
      total += perBox
      total += perBox
      precondition(total == 8 && perBox == 4)
    }
    print("swift-002: passed")
  }
}
```

**Observe:** The accumulator becomes 8 while the fixed amount remains 4.

### Example B: Convert before division

Converting after integer division would preserve the already truncated result.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let whole = 7 / 2
      let fractional = Double(7) / Double(2)
      precondition(whole == 3)
      precondition(fractional == 3.5)
    }
    print("swift-002: passed")
  }
}
```

**Observe:** Integer division yields 3; floating division yields 3.5.

## Exercises

1. **Predict and explain.** Identify the inferred type of every binding.

2. **Guided modification.** Replace an unnecessary var with let and explain why it still compiles.

3. **Independent construction.** Compute a mean from an integer total and count using a deliberate conversion.

4. **Diagnose a defect.** Diagnose conversion performed after integer division.

5. **Boundary evidence.** Test an exactly divisible and a non-divisible pair.

6. **Transfer and justify.** Choose units and types for a small measurement model.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Binding, Type inference, Conversion without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-002: Constants, variables and static types.
Read courses/swift/guides/swift-002.md and courses/swift/lessons/swift-002.swift. Prerequisites: swift-001.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-002_solution.swift and
courses/swift/solutions/swift-002_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
