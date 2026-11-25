# swift-026: Swift packages and module boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-025`

## Learning objectives

Build and run a Swift package and explain its module and target boundaries. The central exercise is task 3: Run swift test and the journey-demo executable.

## Purpose and mental model

A package describes targets, products and dependencies. A target is a compilation unit with a module boundary; a product exposes something consumers can build or import. Splitting a domain library from an executable lets tests and an app share the same core without duplicating source.

The single-file pad cannot accept Package.swift or install dependencies. The checked-in JourneyCore package is a separate complete project with a library, executable and tests, using only the Swift toolchain. Build it deliberately in a prepared environment. Package success on one platform does not establish Apple UI behavior or every deployment architecture.

## Vocabulary and concepts

**Package:** A versioned collection of targets and products.

**Target:** A compilation and dependency unit.

**Module:** A namespace and visibility boundary produced by compilation.

## How to run this lesson

Tasks 2 to 5 run in the separate JourneyCore package lab rather than the pad, so copy the fixture into your own ignored workspace first and keep its build products inside that copy. The two pad examples here show the split between a pure calculation and its presentation; paste them first to confirm the idea before building the package.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Use the complete [JourneyCore project](../fixtures/JourneyCore/README.md). It contains real Package.swift, source and test files and no external package dependencies.

## Syntax anatomy and execution trace

Package.swift declares a tools-version header and target graph. import exposes another module public API. Internal is the usual default access level, while public members define cross-module contracts.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `total` is declared inside `main` and depends only on its argument. `[2, 3].reduce(0, +)` starts at 0, adds 2 and then 3, and returns 5. The empty array returns the initial 0 without calling `+`. Because the function reads no global state and performs no input or output, the same call returns the same value in a test target, a command-line executable or an app, which is what makes it a good candidate for a reusable library module.

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

**Trace.** `render` takes an already computed total and builds the string total=5 through interpolation. It performs no arithmetic, so a wrong total cannot be hidden inside formatting code, and a formatting change cannot alter the number. The check compares the exact string. In the package lab the same split appears as a library target for the calculation and an executable target for printing, and moving `render` between targets would require marking what it uses as `public`.

## Exercises

1. **Predict and explain.** Identify the core and presentation responsibilities.

2. **Guided modification.** Build the complete JourneyCore package with swift build.

3. **Independent construction.** Run swift test and the journey-demo executable.

4. **Diagnose a defect.** Diagnose a symbol that is internal when another module needs public access.

5. **Boundary evidence.** Perform a clean package build using only the lab-owned output directory.

6. **Transfer and justify.** Add a new target only when it creates a useful dependency boundary and document that direction.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.

Task 4's failure appears only across a module boundary: inside one file every declaration is visible, so the pad cannot reproduce it. In the package, call a JourneyCore function declared without an access modifier from the demo executable. For a top-level function the compiler reports that it cannot find the name in scope; for a method on a public type it says the method is inaccessible due to its `internal` protection level. Adding `public` to that declaration, and only that one, fixes it.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Keep a pure core function) before changing anything, and confirm its observation: The pure kernel is suitable for a reusable library.
2. Compare Example B (Separate presentation from calculation) with Example A and name the first line whose behavior differs. Its observation is: Presentation is independently testable.
3. Before opening the explanation, check your task 3 attempt (Run swift test and the journey-demo executable) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Name the three kinds of target in JourneyCore and which one may depend on which. Explain the difference between `internal` and `public` and why `internal` is the default. Say what `swift package clean` removes and what it never touches, and why the build directory belongs inside the copied package.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://www.swift.org/documentation/package-manager/): The Swift Package Manager documentation on swift.org explains package manifests, targets and products; the Swift book's Access Control chapter covers modules.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
