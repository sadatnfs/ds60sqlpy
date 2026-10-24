# swift-039: App architecture: a portable domain core

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-038`

## Learning objectives

Build and test JourneyCore before opening the Apple app. Then draw the dependency direction among core, persistence adapter, view model and SwiftUI views.

## Purpose and mental model

An app is a set of responsibilities with different lifetimes: domain rules, presentation state, views, persistence and external services. A portable domain core lets Linux tests establish business behavior independently of Apple UI rendering. The app adapter then translates user actions into core operations and renders their outcomes.

The JourneyCore package and JourneyApp fixture implement this separation with a small study planner. A lesson item has stable identity, title and completion state. The core rejects empty titles and duplicate identities. SwiftUI presents and edits those values on Apple platforms. Linux can compile and test the core, but cannot qualify view layout, accessibility or simulator behavior.

## Vocabulary and concepts

**Domain core:** Portable rules independent of UI frameworks.

**Reducer:** A function computing next state from current state and an action.

**Presentation state:** Values a view needs to explain current application behavior.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Use [JourneyCore](../fixtures/JourneyCore/README.md) for the complete portable package and [JourneyApp](../fixtures/JourneyApp/README.md) for the real SwiftUI app files and Xcode workflow.

## Syntax anatomy and execution trace

A struct model conforms to Identifiable, Codable, Equatable and Sendable where appropriate. A pure reducer maps a state plus action to a new state. The app owns presentation and storage adapters.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Apply a domain action

A pure transition supports undo, testing and separate UI rendering.

```swift
import Foundation

struct PlannerItem: Equatable, Sendable { let id: String; let title: String; var completed: Bool }
func toggled(_ item: PlannerItem) -> PlannerItem { var result = item; result.completed.toggle(); return result }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let original = PlannerItem(id: "one", title: "Read", completed: false)
            let changed = toggled(original)
            precondition(changed.completed && !original.completed)
        }
        print("swift-039: passed")
    }
}
```

**Observe:** The transformed item changes completion while retaining the original value.

### Example B: Keep identity stable during edits

Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item.

```swift
import Foundation

struct PlannerItem: Equatable, Sendable { let id: String; let title: String; var completed: Bool }
func toggled(_ item: PlannerItem) -> PlannerItem { var result = item; result.completed.toggle(); return result }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let original = PlannerItem(id: "one", title: "Read", completed: false)
            let changed = toggled(original)
            precondition(changed.id == original.id && changed.title == original.title)
        }
        print("swift-039: passed")
    }
}
```

**Observe:** Completion changes do not manufacture a new identity.

## Exercises

1. **Predict and explain.** Identify domain and presentation responsibilities.

2. **Guided modification.** Add a pure rename operation with nonempty-title validation.

3. **Independent construction.** Build and test JourneyCore before opening the Apple app.

4. **Diagnose a defect.** Diagnose placing file access directly inside a model property getter.

5. **Boundary evidence.** Test unknown identity and duplicate identity admission.

6. **Transfer and justify.** Draw the dependency direction among core, persistence adapter, view model and SwiftUI views.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Domain core, Reducer, Presentation state without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-039: App architecture: a portable domain core.
Read courses/swift/guides/swift-039.md and courses/swift/lessons/swift-039.swift. Prerequisites: swift-038.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-039_solution.swift and
courses/swift/solutions/swift-039_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
