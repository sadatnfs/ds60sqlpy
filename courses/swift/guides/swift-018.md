# swift-018: Generics and relationships between types

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-017`

## Learning objectives

Create a generic immutable triple with a rotation operation. Then choose generic or existential abstraction for an API that must preserve concrete result type.

## Purpose and mental model

Generics preserve type relationships across an algorithm or container. A generic pair stores two values of the same chosen type. The compiler rejects mixing unrelated types unless the API explicitly models that possibility. This is stronger and clearer than storing Any and casting later.

Constraints expose the capabilities an algorithm needs. Comparable permits ordering, while Equatable permits equality. Use the narrowest useful constraint and state behavior for ties and empty inputs. Generic abstraction is valuable when it removes duplicated mechanisms without erasing domain meaning.

## Vocabulary and concepts

**Generic parameter:** A type placeholder constrained at compile time.

**Constraint:** A required capability for a type argument.

**Type relationship:** A connection between input, stored and output types.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`func larger<T: Comparable>` introduces a constrained type parameter. The return type T preserves the input relationship. Generic structs use the same parameter syntax.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Reuse an ordering mechanism

The Comparable requirement makes ordering available without dynamic casts.

```swift
import Foundation

func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }
struct Pair<T> {
  let first: T
  let second: T
  func swapped() -> Pair<T> { Pair(first: second, second: first) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      precondition(larger(3, 8) == 8)
      precondition(larger("apple", "pear") == "pear")
    }
    print("swift-018: passed")
  }
}
```

**Observe:** One implementation preserves Int and String results.

### Example B: Preserve container element type

The relationship is encoded in the type rather than a runtime convention.

```swift
import Foundation

func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }
struct Pair<T> {
  let first: T
  let second: T
  func swapped() -> Pair<T> { Pair(first: second, second: first) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let pair = Pair(first: "left", second: "right")
      let swapped = pair.swapped()
      precondition(swapped.first == "right" && swapped.second == "left")
    }
    print("swift-018: passed")
  }
}
```

**Observe:** Swapping retains the same concrete element type.

## Exercises

1. **Predict and explain.** Identify inferred generic types at every call.

2. **Guided modification.** Use larger with Double values and a tie.

3. **Independent construction.** Create a generic immutable triple with a rotation operation.

4. **Diagnose a defect.** Diagnose calling an unavailable method on an unconstrained T.

5. **Boundary evidence.** State tie behavior and test equal inputs.

6. **Transfer and justify.** Choose generic or existential abstraction for an API that must preserve concrete result type.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Generic parameter, Constraint, Type relationship without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-018: Generics and relationships between types.
Read courses/swift/guides/swift-018.md and courses/swift/lessons/swift-018.swift. Prerequisites: swift-017.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-018_solution.swift and
courses/swift/solutions/swift-018_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
