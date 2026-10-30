# swift-001: A Swift source file and its explicit entrypoint

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: None. Begin with the source file and visible result.

## Learning objectives

Compute the capacity of three shelves holding eight books each. Then model a three-level capacity calculation and explain every intermediate value.

## Purpose and mental model

Swift is a compiled language used for portable tools and for applications built with platform frameworks. The language, its standard library and Apple user-interface frameworks are separate layers. A Linux Swift compiler can execute language and portable Foundation code. It does not provide SwiftUI or an iPhone simulator.

The classroom stages one main.swift file and compiles it in Swift 6 mode. An explicit @main type tells the compiler where execution begins. The wrapper uses an asynchronous throwing main so later lessons can keep the same shape. For now, statements execute in order. A compiler error means the program never reached main; a failed precondition means execution reached a violated assumption.

## Vocabulary and concepts

**Source:** The text submitted to a compiler.

**Entrypoint:** The operation called to begin execution.

**Precondition:** A required condition checked during execution.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`@main` marks the entrypoint type. `struct LessonMain` names that type. `static func main() async throws` declares its entry method; async and throws are explained in later chapters. `let` binds a value that cannot be reassigned. `print` produces visible output.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Check before printing

The check establishes a specific observation before the program claims completion.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let greeting = "Hello, Swift"
      precondition(greeting.count == 12)
      print(greeting)
    }
    print("swift-001: passed")
  }
}
```

**Observe:** Hello, Swift appears before the lesson marker.

### Example B: Compute an observable result

The second condition rejects the plausible mistake of adding dimensions instead of multiplying them.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let rows = 4
      let seatsPerRow = 6
      let seats = rows * seatsPerRow
      precondition(seats == 24)
      precondition(seats != rows + seatsPerRow)
    }
    print("swift-001: passed")
  }
}
```

**Observe:** The computed seat count is 24.

## Exercises

1. **Predict and explain.** Predict the greeting count before execution.

2. **Guided modification.** Change the greeting and independently recount its characters.

3. **Independent construction.** Compute the capacity of three shelves holding eight books each.

4. **Diagnose a defect.** Remove a closing brace temporarily and classify the failure as compilation.

5. **Boundary evidence.** Check zero shelves and one shelf.

6. **Transfer and justify.** Model a three-level capacity calculation and explain every intermediate value.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Do not delete a failed precondition to reach the marker. Preserve the first compiler diagnostic before interpreting later errors. The entrypoint wrapper is required by this classroom compile contract.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Source, Entrypoint, Precondition without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-001: A Swift source file and its explicit entrypoint.
Read courses/swift/guides/swift-001.md and courses/swift/lessons/swift-001.swift. Prerequisites: none.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-001_solution.swift and
courses/swift/solutions/swift-001_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
