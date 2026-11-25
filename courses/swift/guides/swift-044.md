# swift-044: Accessibility, localization and inclusive interaction

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-043`

## Learning objectives

Make an app accessible and localizable with meaningful labels and stable identity. The central exercise is task 3: Run JourneyApp using keyboard navigation and VoiceOver on macOS.

## Purpose and mental model

An app is not complete when it looks correct in one screenshot. Users navigate with keyboards, screen readers, large text, reduced motion and different language conventions. A meaningful control needs an accessible name and state. Color alone cannot communicate completion or error.

Localization separates user-facing text from program identity. Keep stable IDs independent of translated titles, and avoid assembling sentences from fragments whose order may differ across languages. The app fixture uses semantic buttons, text labels, accessibility identifiers for tests and a clear completion label. Real VoiceOver, keyboard and Dynamic Type verification remains an Apple-platform task.

## Vocabulary and concepts

**Accessible name:** The label assistive technology uses for a control.

**Dynamic Type:** User-selected text sizing supported by Apple UI systems.

**Localization:** Adapting text and presentation to a language and region.

## How to run this lesson

The pad checks only the text policy, since speaking and rendering require the Apple app. Tasks 3 and 5 need JourneyApp on macOS with VoiceOver and large text; record what you actually heard and saw, including defects, rather than what the code suggests should happen.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The [JourneyApp acceptance guide](../fixtures/JourneyApp/README.md) includes keyboard, VoiceOver, large-text and reduced-motion observations to record.

## Syntax anatomy and execution trace

In SwiftUI, accessibilityLabel and accessibilityValue describe semantics; accessibilityIdentifier is a testing hook, not a spoken label substitute. Localized strings and format styles should preserve plural and locale rules.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Describe state with words

A textual state remains meaningful when a visual marker is unavailable.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func accessibilityText(title: String, complete: Bool) -> String {
        "\(title), \(complete ? "complete" : "incomplete")"
      }
      precondition(accessibilityText(title: "Read", complete: true) == "Read, complete")
    }
    print("swift-044: passed")
  }
}
```

**Observe:** The label communicates completion without relying on color.

**Trace.** `accessibilityText` takes a title and a Boolean. The conditional inside the interpolation picks complete for true, and the result is Read, complete. The check compares the exact string. A screen reader would speak this text, so the completion state reaches the user as a word even when the visual marker is a color or icon they cannot perceive.

### Example B: Keep identity separate from translation

Saved work and navigation should not break when a learner changes language.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let titles = ["en": "Read", "fr": "Lire"]
      let saved: [String: Bool] = ["lesson-one": true]
      func row(id: String, language: String) -> String {
        let state = saved[id] == true ? "complete" : "incomplete"
        return "\(titles[language] ?? id): \(state)"
      }
      precondition(row(id: "lesson-one", language: "en") == "Read: complete")
      precondition(row(id: "lesson-one", language: "fr") == "Lire: complete")
    }
    print("swift-044: passed")
  }
}
```

**Observe:** Switching language changes the title from Read to Lire while the completion saved under lesson-one still shows complete.

**Trace.** `saved` maps the stable identifier lesson-one to true. `row` looks up the completion state by identifier and the display title by language. For English, the title is Read and the state is complete. For French, the title is Lire, but the lookup still uses lesson-one and finds the same saved state. If the saved key had been the English title, switching to French would have lost the progress.

## Exercises

1. **Predict and explain.** Identify which information would be lost without color.

2. **Guided modification.** Write an accessible label for an incomplete item and its action.

3. **Independent construction.** Run JourneyApp using keyboard navigation and VoiceOver on macOS.

4. **Diagnose a defect.** Diagnose using a testing identifier as the only meaningful accessibility label.

5. **Boundary evidence.** Check large text, empty content and long translated titles in the Apple project.

6. **Transfer and justify.** Create a manual accessibility acceptance checklist with concrete observations and retained defects.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.

For task 2, an incomplete item needs both a state and an action, such as Read, incomplete and a Mark complete button; a label without the action leaves the user unsure what activating it does. Task 4's identifier is never spoken, so a control labeled only by its testing identifier is announced without a meaningful name. Missing titles fall back to the identifier, which you should check deliberately.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Describe state with words) before changing anything, and confirm its observation: The label communicates completion without relying on color.
2. Compare Example B (Keep identity separate from translation) with Example A and name the first line whose behavior differs. Its observation is: Switching language changes the title from Read to Lire while the completion saved under lesson-one still shows complete.
3. Before opening the explanation, check your task 3 attempt (Run JourneyApp using keyboard navigation and VoiceOver on macOS) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain the difference between an accessibility label, an accessibility value and an accessibility identifier. Say why saved progress must be keyed by a stable identifier. Name three observations your manual checklist must record for large text, and what to do with a defect you cannot fix now.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://developer.apple.com/documentation/swiftui/accessibility): Apple's SwiftUI accessibility documentation covers labels, values and identifiers; the Human Interface Guidelines describe VoiceOver and Dynamic Type.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
