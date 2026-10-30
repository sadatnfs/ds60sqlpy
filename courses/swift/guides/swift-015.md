# swift-015: Closures, captures and transformation pipelines

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-014`

## Learning objectives

Write a function accepting a transformation closure. Then choose a named function or closure for a reusable domain transformation and explain readability and capture policy.

## Purpose and mental model

A closure is executable behavior that can be passed as a value. It can capture surrounding variables, which lets it remember context but can also create surprising mutation or lifetime relationships. Swift capture lists can copy a value at closure creation or weaken a reference, depending on the declared policy.

Map transforms each element while filter selects elements. These operations express intent when the closure remains small and clear. Avoid compressing a complex domain algorithm into a chain whose intermediate states nobody can inspect. Name important transformations and preserve a traceable failure boundary.

## Vocabulary and concepts

**Closure:** Callable behavior that may carry surrounding context.

**Capture list:** An explicit policy for captured values or references.

**Higher-order function:** A function that accepts or returns functions.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`{ value in value * 2 }` is a closure. `$0` abbreviates its first argument. A capture list such as `[factor]` captures the current value. Function types use `(Input) -> Output`.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Transform a sequence

The transformation is pure and its element-to-element relationship is visible.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [1, 2, 3]
      let doubled = values.map { value in value * 2 }
      precondition(doubled == [2, 4, 6])
      precondition(values == [1, 2, 3])
    }
    print("swift-015: passed")
  }
}
```

**Observe:** Map creates transformed values while retaining the original array.

### Example B: Freeze a captured value deliberately

This differs from a closure observing a mutable captured variable later.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      var factor = 2
      let scale = { [factor] (value: Int) in value * factor }
      factor = 5
      precondition(scale(3) == 6 && factor == 5)
    }
    print("swift-015: passed")
  }
}
```

**Observe:** The explicit capture list retains factor 2 for the closure.

## Exercises

1. **Predict and explain.** Predict the mapped result and unchanged source.

2. **Guided modification.** Filter even numbers before mapping.

3. **Independent construction.** Write a function accepting a transformation closure.

4. **Diagnose a defect.** Diagnose a closure whose captured mutable state changes before later execution.

5. **Boundary evidence.** Test empty arrays and a closure that returns an optional.

6. **Transfer and justify.** Choose a named function or closure for a reusable domain transformation and explain readability and capture policy.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Closure, Capture list, Higher-order function without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-015: Closures, captures and transformation pipelines.
Read courses/swift/guides/swift-015.md and courses/swift/lessons/swift-015.swift. Prerequisites: swift-014.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-015_solution.swift and
courses/swift/solutions/swift-015_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
