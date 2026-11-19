# swift-008: Functions, argument labels and value contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-007`

## Learning objectives

Write functions with clear argument labels and choose between value parameters and inout. The central exercise is task 3: Write a pure function normalizing a quantity without mutating its caller.

## Purpose and mental model

A function groups a computation behind a contract. Swift distinguishes the argument label read at the call site from the parameter name used inside the body. Labels can make an API read as a clear operation rather than an unexplained list of positional values. Use the underscore label only when the surrounding context already makes the meaning clear.

Ordinary value arguments are passed with value semantics. An inout parameter explicitly grants temporary mutation of the caller value under Swift exclusivity rules. Prefer returned values for pure transformations and use inout when mutation is the actual interface. A function contract should state invalid-input behavior and whether any state changes before failure.

## Vocabulary and concepts

**Argument label:** The name used at the call site.

**Parameter:** The local name of an input inside a function.

**Inout:** Explicit temporary mutable access to a caller value.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`func area(width: Int, height: Int) -> Int` exposes labels. `_ value` removes the external label. `inout` in a declaration pairs with `&` at the call site. `return` supplies the result and exits.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Name the dimensions

Readable call sites reduce accidental parameter swaps and reveal the function purpose.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func area(width: Int, height: Int) -> Int { width * height }
      precondition(area(width: 3, height: 4) == 12)
      precondition(area(width: 0, height: 4) == 0)
    }
    print("swift-008: passed")
  }
}
```

**Observe:** Labels show which dimension each argument supplies.

### Example B: Make mutation explicit

The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func increment(_ value: inout Int) { value += 1 }
      var count = 4
      increment(&count)
      precondition(count == 5)
    }
    print("swift-008: passed")
  }
}
```

**Observe:** The caller explicitly grants mutation and observes 5.

## Exercises

1. **Predict and explain.** Explain each argument label and local parameter name.

2. **Guided modification.** Add a depth label for a volume function.

3. **Independent construction.** Write a pure function normalizing a quantity without mutating its caller.

4. **Diagnose a defect.** Diagnose an inout call missing the ampersand and explain the compiler rule.

5. **Boundary evidence.** Test zero and negative dimensions under a documented validation policy.

6. **Transfer and justify.** Choose return values or inout for an API and justify who owns state changes.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. The separate explanation gives an executed reference answer where one has been written and says plainly where none exists yet. Open it only after your own attempt, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Reproduce Example A (Name the dimensions) before changing anything, and confirm its observation: Labels show which dimension each argument supplies.
2. Compare Example B (Make mutation explicit) with Example A and name the first line whose behavior differs. Its observation is: The caller explicitly grants mutation and observes 5.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Labels are part of API usability.

## Self-check and next step

Explain Argument label, Parameter, Inout without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-008: Functions, argument labels and value contracts.
Read courses/swift/guides/swift-008.md and courses/swift/lessons/swift-008.swift. Prerequisites: swift-007.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-008_solution.swift and
courses/swift/solutions/swift-008_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
