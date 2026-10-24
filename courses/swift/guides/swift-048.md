# swift-048: Capstone: an offline-first study planner

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-047`

## Learning objectives

Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination. Then deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.

## Purpose and mental model

The final project connects a portable domain package, a SwiftUI application, stable navigation, editable state and versioned persistence. It remains offline by default so a learner can inspect every meaningful behavior without credentials or a remote service. The architecture has deliberate extension points for networking and additional data models.

A complete capstone includes evidence and limits. Explain which invariants the Linux kernel establishes, which package tests ran, which Apple destination rendered the UI and how saved-state recovery was checked. Keep an unsuccessful observation visible until it is resolved. Expertise grows through independent extensions and diagnosis, not through copying the final source or declaring every possible app scenario covered.

## Vocabulary and concepts

**Offline-first:** Core behavior works without a network dependency.

**Acceptance evidence:** Recorded observations establishing a declared requirement.

**Extension boundary:** A documented place for adding behavior without duplicating core rules.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Start from the actual [JourneyCore](../fixtures/JourneyCore/README.md) and [JourneyApp](../fixtures/JourneyApp/README.md) project files. The app project includes working list, detail editing, navigation, save/load and platform text-bridge code.

## Syntax anatomy and execution trace

A stable item identity connects domain actions, navigation and saved data. A reducer updates values; a MainActor presentation model owns view state; a persistence adapter encodes the versioned document. Each layer has its own test boundary.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Produce a stable completion summary

The report checks state and identity rather than only a formatted label.

```swift
import Foundation

struct CapstoneItem: Equatable, Sendable { let id: String; var complete: Bool }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let items = [CapstoneItem(id: "a", complete: true), CapstoneItem(id: "b", complete: false)]
            precondition(items.filter(\.complete).count == 1)
            precondition(Set(items.map(\.id)).count == items.count)
        }
        print("swift-048: passed")
    }
}
```

**Observe:** One of two uniquely identified items is complete.

### Example B: Preserve identity across a value update

These are the core semantics needed by undo, navigation and persistence.

```swift
import Foundation

struct CapstoneItem: Equatable, Sendable { let id: String; var complete: Bool }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let original = CapstoneItem(id: "a", complete: false)
            var changed = original
            changed.complete = true
            precondition(changed.id == original.id && !original.complete && changed.complete)
        }
        print("swift-048: passed")
    }
}
```

**Observe:** The update retains identity and the prior snapshot.

## Exercises

1. **Predict and explain.** Trace one user action from view through model to domain state.

2. **Guided modification.** Add a derived progress summary without duplicating stored completion counts.

3. **Independent construction.** Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.

4. **Diagnose a defect.** Introduce and repair a stale-binding, duplicate-identity or failed-save defect.

5. **Boundary evidence.** Verify empty state, long titles, duplicate IDs, malformed storage and save/reload.

6. **Transfer and justify.** Deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Offline-first, Acceptance evidence, Extension boundary without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-048: Capstone: an offline-first study planner.
Read courses/swift/guides/swift-048.md and courses/swift/lessons/swift-048.swift. Prerequisites: swift-047.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-048_solution.swift and
courses/swift/solutions/swift-048_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
