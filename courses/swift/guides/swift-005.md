# swift-005: Optionals and honest absence

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-004`

## Learning objectives

Write a parser accepting only present nonnegative integers. Then model an optional measurement whose absence must survive serialization and reporting.

## Purpose and mental model

An optional represents either a wrapped value or no value. This makes absence part of the type rather than an undocumented sentinel. Int zero can be a real measurement, so it should not also mean missing. Optional binding introduces a nonoptional value only inside the branch where presence has been established.

A force unwrap asserts that absence is impossible and traps if that assertion is wrong. It is suitable for tightly controlled fixture literals but is usually a poor external-input policy. Prefer if let for branching and guard let for an early-exit precondition. A fallback with ?? is valid only when the domain really assigns that replacement meaning.

## Vocabulary and concepts

**Optional:** A value that may be present or absent.

**Unwrapping:** Accessing a wrapped value after establishing presence.

**Nil:** The absent optional case.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Int?` abbreviates Optional<Int>. `if let value = optional` unwraps on the present branch. `guard let` requires an early exit on failure. `??` selects a fallback only when the optional is nil.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Preserve zero as a value

The branch proves presence before the wrapped integer is used.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let measured: Int? = 0
      let missing: Int? = nil
      precondition(measured != nil && missing == nil)
      if let value = measured {
        precondition(value == 0)
      } else {
        preconditionFailure("present zero")
      }
    }
    print("swift-005: passed")
  }
}
```

**Observe:** A present zero remains distinct from nil.

### Example B: Parse with an absence policy

The fallback is an explicit display sentinel in this fixture, not a valid quantity.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let valid = Int("42")
      let invalid = Int("forty-two")
      precondition(valid == 42 && invalid == nil)
      precondition((invalid ?? -1) == -1)
    }
    print("swift-005: passed")
  }
}
```

**Observe:** Parsing produces an optional and malformed text is absent.

## Exercises

1. **Predict and explain.** Explain the difference between nil and a wrapped zero.

2. **Guided modification.** Replace the display sentinel with an unknown label.

3. **Independent construction.** Write a parser accepting only present nonnegative integers.

4. **Diagnose a defect.** Diagnose force-unwrapping malformed external text.

5. **Boundary evidence.** Test empty, zero, negative and out-of-range input.

6. **Transfer and justify.** Model an optional measurement whose absence must survive serialization and reporting.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Optional, Unwrapping, Nil without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-005: Optionals and honest absence.
Read courses/swift/guides/swift-005.md and courses/swift/lessons/swift-005.swift. Prerequisites: swift-004.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-005_solution.swift and
courses/swift/solutions/swift-005_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
