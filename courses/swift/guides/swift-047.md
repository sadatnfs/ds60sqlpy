# swift-047: Multiplatform design and deployment contracts

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-046`

## Learning objectives

Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS. Then create a platform support matrix listing compiled, executed and manually inspected surfaces separately.

## Purpose and mental model

Sharing Swift code does not mean every platform has the same frameworks or user expectations. A domain package can compile on Linux and Apple platforms, while UI adapters differ. Conditional compilation is useful at a narrow boundary; scattering platform checks throughout domain logic makes the core harder to reason about.

Deployment targets state the oldest platform APIs an app promises to support. Runtime availability checks can gate newer functionality, but the fallback must still be useful. Resource paths, permissions and application lifecycle also vary. Treat cross-platform support as a matrix of actual builds and runs, not a claim inferred from the language name.

## Vocabulary and concepts

**Deployment target:** The oldest platform version an artifact intends to support.

**Conditional compilation:** Selecting source at compile time under explicit conditions.

**Platform adapter:** A layer isolating platform-specific mechanisms.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The portable [JourneyCore](../fixtures/JourneyCore/README.md) and Apple-only [JourneyApp](../fixtures/JourneyApp/README.md) establish the intended boundary.

## Syntax anatomy and execution trace

#if canImport selects compile-time framework availability. #available guards runtime API availability on Apple platforms. Package platform declarations and Xcode deployment settings are related project contracts.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Identify which code belongs in the portable core.

2. **Guided modification.** Add a platform-neutral derived statistic.

3. **Independent construction.** Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.

4. **Diagnose a defect.** Diagnose importing UIKit in a shared domain target.

5. **Boundary evidence.** Test unavailable capabilities with a clear message rather than a broken Run action.

6. **Transfer and justify.** Create a platform support matrix listing compiled, executed and manually inspected surfaces separately.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Deployment target, Conditional compilation, Platform adapter without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://www.swift.org/platform-support/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
