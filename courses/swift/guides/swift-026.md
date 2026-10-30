# swift-026: Swift packages and module boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-025`

## Learning objectives

Run swift test and the journey-demo executable. Then add a new target only when it creates a useful dependency boundary and document that direction.

## Purpose and mental model

A package describes targets, products and dependencies. A target is a compilation unit with a module boundary; a product exposes something consumers can build or import. Splitting a domain library from an executable lets tests and an app share the same core without duplicating source.

The single-file pad cannot accept Package.swift or install dependencies. The checked-in JourneyCore package is a separate complete project with a library, executable and tests, using only the Swift toolchain. Build it deliberately in a prepared environment. Package success on one platform does not establish Apple UI behavior or every deployment architecture.

## Vocabulary and concepts

**Package:** A versioned collection of targets and products.

**Target:** A compilation and dependency unit.

**Module:** A namespace and visibility boundary produced by compilation.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Use the complete [JourneyCore project](../fixtures/JourneyCore/README.md). It contains real Package.swift, source and test files and no external package dependencies.

## Syntax anatomy and execution trace

Package.swift declares a tools-version header and target graph. import exposes another module public API. Internal is the usual default access level, while public members define cross-module contracts.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Keep a pure core function

A portable contract can be shared by an executable, tests and a later app adapter.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func total(_ values: [Int]) -> Int { values.reduce(0, +) }
      precondition(total([2, 3]) == 5)
      precondition(total([]) == 0)
    }
    print("swift-026: passed")
  }
}
```

**Observe:** The pure kernel is suitable for a reusable library.

### Example B: Separate presentation from calculation

Moving this function into another target requires a deliberate public interface rather than copying implementation text.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func render(_ total: Int) -> String { "total=\(total)" }
      precondition(render(5) == "total=5")
    }
    print("swift-026: passed")
  }
}
```

**Observe:** Presentation is independently testable.

## Exercises

1. **Predict and explain.** Identify the core and presentation responsibilities.

2. **Guided modification.** Build the complete JourneyCore package with swift build.

3. **Independent construction.** Run swift test and the journey-demo executable.

4. **Diagnose a defect.** Diagnose a symbol that is internal when another module needs public access.

5. **Boundary evidence.** Perform a clean package build using only the lab-owned output directory.

6. **Transfer and justify.** Add a new target only when it creates a useful dependency boundary and document that direction.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Package, Target, Module without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://www.swift.org/documentation/package-manager/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-026: Swift packages and module boundaries.
Read courses/swift/guides/swift-026.md and courses/swift/lessons/swift-026.swift. Prerequisites: swift-025.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-026_solution.swift and
courses/swift/solutions/swift-026_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
