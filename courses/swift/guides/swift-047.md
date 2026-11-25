# swift-047: Multiplatform design and deployment contracts

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-046`

## Learning objectives

Separate portable and platform-specific code and state each platform's deployment contract. The central exercise is task 3: Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.

## Purpose and mental model

Sharing Swift code does not mean every platform has the same frameworks or user expectations. A domain package can compile on Linux and Apple platforms, while UI adapters differ. Conditional compilation is useful at a narrow boundary; scattering platform checks throughout domain logic makes the core harder to reason about.

Deployment targets state the oldest platform APIs an app promises to support. Runtime availability checks can gate newer functionality, but the fallback must still be useful. Resource paths, permissions and application lifecycle also vary. Treat cross-platform support as a matrix of actual builds and runs, not a claim inferred from the language name.

## Vocabulary and concepts

**Deployment target:** The oldest platform version an artifact intends to support.

**Conditional compilation:** Selecting source at compile time under explicit conditions.

**Platform adapter:** A layer isolating platform-specific mechanisms.

## How to run this lesson

Both checks run on Linux because they use only the standard library. Task 3 builds JourneyCore on Linux and JourneyApp separately on macOS, so record which machine produced each result. `#if canImport` decides at compile time, while `#available` checks the running OS version on Apple platforms.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The portable [JourneyCore](../fixtures/JourneyCore/README.md) and Apple-only [JourneyApp](../fixtures/JourneyApp/README.md) establish the intended boundary.

## Syntax anatomy and execution trace

#if canImport selects compile-time framework availability. #available guards runtime API availability on Apple platforms. Package platform declarations and Xcode deployment settings are related project contracts.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Keep portable policy independent

A portable core should not import a platform framework merely to format its basic domain outcome.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func summary(completed: Int, total: Int) -> String { "\(completed)/\(total) complete" }
      precondition(summary(completed: 2, total: 3) == "2/3 complete")
    }
    print("swift-047: passed")
  }
}
```

**Observe:** The same domain summary works without a UI framework.

**Trace.** `summary` interpolates two integers into the text 2/3 complete. It uses only `String` interpolation, which is part of the standard library on every platform, so the same function compiles in JourneyCore on Linux and inside the Apple app. The check compares the exact string. If formatting needed locale rules, that richer presentation could live in the app layer.

### Example B: Declare a capability rather than guess

Capability descriptions should follow actual prepared runtime evidence.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let capabilities = Set(["portable-core", "foundation-files"])
      precondition(capabilities.contains("portable-core"))
      precondition(!capabilities.contains("swiftui-linux"))
    }
    print("swift-047: passed")
  }
}
```

**Observe:** The Linux capability set does not invent SwiftUI support.

**Trace.** `capabilities` lists what the Linux environment actually provides. The first check confirms the portable core is present; the second confirms swiftui-linux is absent, because SwiftUI is not available on Linux. A support statement built from a set like this cannot claim a capability that was never observed. The app should show a clear message for an absent capability instead of a Run action that fails.

## Exercises

1. **Predict and explain.** Identify which code belongs in the portable core.

2. **Guided modification.** Add a platform-neutral derived statistic.

3. **Independent construction.** Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.

4. **Diagnose a defect.** Diagnose importing UIKit in a shared domain target.

5. **Boundary evidence.** Test unavailable capabilities with a clear message rather than a broken Run action.

6. **Transfer and justify.** Create a platform support matrix listing compiled, executed and manually inspected surfaces separately.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.

Task 4's shared target imports UIKit, which builds for iOS but fails on macOS and Linux with a message that no such module exists. The counterexample is running `swift build` for JourneyCore on Linux after adding the import. Moving the import into the app target, or guarding it with `#if canImport(UIKit)`, restores the portable build.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Keep portable policy independent) before changing anything, and confirm its observation: The same domain summary works without a UI framework.
2. Compare Example B (Declare a capability rather than guess) with Example A and name the first line whose behavior differs. Its observation is: The Linux capability set does not invent SwiftUI support.
3. Before opening the explanation, check your task 3 attempt (Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain the difference between `#if canImport` and `#available`. Say which JourneyCore code would break if it imported SwiftUI. For your support matrix, define compiled, executed and manually inspected, and say why each surface needs its own column. Then place `summary` in the matrix and justify its row.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://www.swift.org/platform-support/): The Swift language reference covers conditional compilation and availability conditions; the Swift Package Manager documentation covers platform declarations.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-047: Multiplatform design and deployment contracts.
Read courses/swift/guides/swift-047.md and courses/swift/lessons/swift-047.swift. Prerequisites: swift-046.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-047_solution.swift and
courses/swift/solutions/swift-047_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
