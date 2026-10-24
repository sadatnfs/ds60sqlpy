# swift-044: Accessibility, localization and inclusive interaction

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-043`

## Learning objectives

Run JourneyApp using keyboard navigation and VoiceOver on macOS. Then create a manual accessibility acceptance checklist with concrete observations and retained defects.

## Purpose and mental model

An app is not complete when it looks correct in one screenshot. Users navigate with keyboards, screen readers, large text, reduced motion and different language conventions. A meaningful control needs an accessible name and state. Color alone cannot communicate completion or error.

Localization separates user-facing text from program identity. Keep stable IDs independent of translated titles, and avoid assembling sentences from fragments whose order may differ across languages. The app fixture uses semantic buttons, text labels, accessibility identifiers for tests and a clear completion label. Real VoiceOver, keyboard and Dynamic Type verification remains an Apple-platform task.

## Vocabulary and concepts

**Accessible name:** The label assistive technology uses for a control.

**Dynamic Type:** User-selected text sizing supported by Apple UI systems.

**Localization:** Adapting text and presentation to a language and region.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The [JourneyApp acceptance guide](../fixtures/JourneyApp/README.md) includes keyboard, VoiceOver, large-text and reduced-motion observations to record.

## Syntax anatomy and execution trace

In SwiftUI, accessibilityLabel and accessibilityValue describe semantics; accessibilityIdentifier is a testing hook, not a spoken label substitute. Localized strings and format styles should preserve plural and locale rules.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Describe state with words

A textual state remains meaningful when a visual marker is unavailable.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            func accessibilityText(title: String, complete: Bool) -> String { "\(title), \(complete ? "complete" : "incomplete")" }
            precondition(accessibilityText(title: "Read", complete: true) == "Read, complete")
        }
        print("swift-044: passed")
    }
}
```

**Observe:** The label communicates completion without relying on color.

### Example B: Keep identity separate from translation

Saved work and navigation should not break when a learner changes language.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let identity = "lesson-one"
            let titles = ["en": "Read", "fr": "Lire"]
            precondition(titles["en"] != titles["fr"])
            precondition(identity == "lesson-one")
        }
        print("swift-044: passed")
    }
}
```

**Observe:** Display text changes while identity remains stable.

## Exercises

1. **Predict and explain.** Identify which information would be lost without color.

2. **Guided modification.** Write an accessible label for an incomplete item and its action.

3. **Independent construction.** Run JourneyApp using keyboard navigation and VoiceOver on macOS.

4. **Diagnose a defect.** Diagnose using a testing identifier as the only meaningful accessibility label.

5. **Boundary evidence.** Check large text, empty content and long translated titles in the Apple project.

6. **Transfer and justify.** Create a manual accessibility acceptance checklist with concrete observations and retained defects.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Accessible name, Dynamic Type, Localization without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://developer.apple.com/documentation/swiftui/accessibility). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-044: Accessibility, localization and inclusive interaction.
Read courses/swift/guides/swift-044.md and courses/swift/lessons/swift-044.swift. Prerequisites: swift-043.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-044_solution.swift and
courses/swift/solutions/swift-044_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
